from __future__ import annotations
import json
import math
from typing import Any, Dict, List, Optional

# Reuse your database connection helper functions
from common import fetch_all, fetch_one

# ---------- HTTP helpers ----------
DEFAULT_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Requested-With",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}

def _resp(status: int, body: Any):
    return {
        "statusCode": status,
        "headers": DEFAULT_HEADERS,
        "isBase64Encoded": False,
        "body": json.dumps(body, ensure_ascii=False),
    }

def _extract_query_params(event: Dict[str, Any]) -> Dict[str, str]:
    """Extract query parameters"""
    return event.get("queryStringParameters") or {}

def _to_int(s: Optional[str], default: int) -> int:
    try:
        return int(s) if s is not None else default
    except Exception:
        return default

# ---------- Plant list query SQL ----------
PLANTS_LIST_SQL = """
    SELECT 
        ID,
        Binomial,
        CommonName,
        EPBCStatus,
        IUCNStatus,
        MaxStatus,
        State,
        Region,
        RegionCentroidLatitude,
        RegionCentroidLongitude
    FROM Table16_TSX_SpeciesMonitoringTable 
    WHERE EPBCStatus IS NOT NULL 
      AND EPBCStatus != ''
"""

PLANTS_COUNT_SQL = """
    SELECT COUNT(*) as total
    FROM Table16_TSX_SpeciesMonitoringTable 
    WHERE EPBCStatus IS NOT NULL 
      AND EPBCStatus != ''
"""

def get_plants_list(
    state: Optional[str] = None, 
    page: int = 1, 
    limit: int = 20
) -> Dict[str, Any]:
    """Get plant list with state filtering and pagination support"""
    # Build query conditions
    conditions = []
    params = []
    
    if state and state != "All states":
        conditions.append("State = %s")
        params.append(state)
    
    # Build complete SQL
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    base_sql = PLANTS_LIST_SQL
    count_sql = PLANTS_COUNT_SQL
    
    if conditions:
        base_sql += f" AND {where_clause}"
        count_sql += f" AND {where_clause}"
    
    # Add sorting and pagination
    base_sql += " ORDER BY Binomial ASC LIMIT %s OFFSET %s"
    
    # Calculate pagination offset
    offset = (page - 1) * limit
    query_params = params + [limit, offset]
    
    try:
        # Get total count
        count_result = fetch_one(count_sql, params)
        total_count = count_result.get('total', 0) if count_result else 0
        
        # Get plant list
        rows = fetch_all(base_sql, query_params)
        
        plants = []
        for row in rows:
            plant = {
                "id": row.get('ID'),
                "binomial": row.get('Binomial', ''),
                "commonName": row.get('CommonName', ''),
                "epbcStatus": row.get('EPBCStatus', ''),
                "iucnStatus": row.get('IUCNStatus', ''),
                "maxStatus": row.get('MaxStatus', ''),
                "state": row.get('State', ''),
                "region": row.get('Region', ''),
                "latitude": float(row.get('RegionCentroidLatitude', 0)) if row.get('RegionCentroidLatitude') else None,
                "longitude": float(row.get('RegionCentroidLongitude', 0)) if row.get('RegionCentroidLongitude') else None,
                "thumbnailUrl": f"/images/plants/{row.get('ID')}.jpg"
            }
            plants.append(plant)
        
        # Calculate pagination info
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
        
        return {
            "success": True,
            "plants": plants,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "totalPages": total_pages,
                "hasNext": page < total_pages,
                "hasPrev": page > 1
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Database query failed: {str(e)}",
            "plants": [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": 0,
                "totalPages": 0,
                "hasNext": False,
                "hasPrev": False
            }
        }

# ---------- Lambda main entry point ----------

def lambda_handler(event, context):
    # Extract query parameters
    query_params = _extract_query_params(event)
    
    # Get filter conditions from query parameters
    state = query_params.get("state")
    page = _to_int(query_params.get("page"), 1)
    limit = _to_int(query_params.get("limit"), 20)
    
    # Validate parameters
    if page < 1:
        return _resp(400, {"success": False, "error": "Page number must be greater than 0"})
    if limit < 1 or limit > 100:
        return _resp(400, {"success": False, "error": "Items per page must be between 1-100"})
    
    try:
        data = get_plants_list(state, page, limit)
        return _resp(200, data)
    except Exception as e:
        return _resp(500, {"success": False, "message": f"Internal error: {e}"})
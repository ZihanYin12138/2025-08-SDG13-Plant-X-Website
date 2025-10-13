from __future__ import annotations
import json
import math
import base64
from datetime import date, datetime
from typing import Any, Dict, List, Optional

# Reuse your shared DB helpers
from common import fetch_all, fetch_one, get_connection

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
        "body": json.dumps(body, ensure_ascii=False, default=_serialize_date),
    }

# ---------- Request parsing (supports API Gateway REST v1 & HTTP v2) ----------

def _extract_req(event: Dict[str, Any]) -> tuple[str, str, Dict[str, str], Dict[str, Any]]:
    """Extract request method, path, query parameters and request body"""
    rc = event.get("requestContext") or {}
    http_v2 = rc.get("http") or {}
    
    if http_v2.get("method"):
        # API Gateway HTTP v2
        method = http_v2.get("method", "GET")
        path = http_v2.get("path", "/")
        query_params = event.get("queryStringParameters") or {}
        body = event.get("body", "{}")
    else:
        # API Gateway REST v1
        method = event.get("httpMethod", "GET")
        path = event.get("path", "/")
        query_params = event.get("queryStringParameters") or {}
        body = event.get("body", "{}")
    
    # Debug: print raw request body
    print(f"🔍 Raw request body (type: {type(body)}): {body}")
    
    # Check if Base64 decoding is needed
    is_base64_encoded = event.get("isBase64Encoded", False)
    print(f"🔍 isBase64Encoded: {is_base64_encoded}")
    
    # Process request body
    if is_base64_encoded and body:
        try:
            # Base64 decode
            decoded_body = base64.b64decode(body).decode('utf-8')
            print(f"🔍 After Base64 decode: {decoded_body}")
            body = decoded_body
        except Exception as e:
            print(f"❌ Base64 decode failed: {e}")
    
    # Parse JSON request body
    try:
        parsed_body = json.loads(body) if body else {}
        print(f"✅ JSON parsing successful: {parsed_body}")
    except Exception as e:
        print(f"❌ JSON parsing failed: {e}")
        parsed_body = {}
    
    return method, path, query_params, parsed_body


def _to_int(s: Optional[str], default: int) -> int:
    try:
        return int(s) if s is not None else default
    except Exception:
        return default

def _to_float(s: Optional[str], default: float) -> float:
    try:
        return float(s) if s is not None else default
    except Exception:
        return default

def _serialize_date(obj):
    """Serialize date objects to strings"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj

# ---------- Geospatial calculation functions ----------

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points (meters)"""
    R = 6371000  # Earth radius (meters)
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def normalize_maturity(age_description: Optional[str]) -> str:
    """Normalize maturity description"""
    if not age_description:
        return "Unknown"
    
    s = str(age_description).strip().lower()
    if s in ("juvenile", "young", "sapling", "youth"):
        return "Juvenile"
    if s in ("semi-mature", "semi mature", "semi", "subadult"):
        return "Semi-Mature"
    if s in ("mature", "adult", "established"):
        return "Mature"
    return "Unknown"

def calculate_age(year_planted: Optional[int], reference_year: int = 2025) -> Optional[int]:
    """Calculate tree age"""
    if not year_planted or year_planted < 1500 or year_planted > reference_year:
        return None
    return reference_year - year_planted

def jitter_duplicates(trees: List[Dict[str, Any]], step: float = 0.00002) -> List[Dict[str, Any]]:
    """Add small offset to trees with same coordinates to avoid marker overlap"""
    key_counts = {}
    result = []
    
    for tree in trees:
        lat = tree.get('latitude', 0)
        lon = tree.get('longitude', 0)
        key = (round(float(lat), 6), round(float(lon), 6))
        
        k = key_counts.get(key, 0)
        key_counts[key] = k + 1
        
        if k == 0:
            result.append(tree)
        else:
            # Add offset
            direction = k % 4
            ring = (k // 4) + 1
            offset = ring * step
            
            new_tree = tree.copy()
            if direction == 0:  # East
                new_tree['longitude'] = lon + offset
            elif direction == 1:  # West
                new_tree['longitude'] = lon - offset
            elif direction == 2:  # North
                new_tree['latitude'] = lat + offset
            else:  # South
                new_tree['latitude'] = lat - offset
            
            result.append(new_tree)
    
    return result


# ---------- Tree search SQL ----------
TREE_SEARCH_SQL = """
    SELECT 
        com_id,
        common_name,
        scientific_name,
        genus,
        family,
        diameter_breast_height,
        year_planted,
        date_planted,
        age_description,
        useful_life_expectency,
        useful_life_expectency_value,
        located_in,
        uploaddate,
        latitude,
        longitude
    FROM Table12_UrbanForestTable
    WHERE latitude IS NOT NULL 
      AND longitude IS NOT NULL
      AND latitude BETWEEN %s AND %s
      AND longitude BETWEEN %s AND %s
"""

# ---------- Tree details SQL ----------
TREE_DETAIL_SQL = """
    SELECT 
        com_id,
        common_name,
        scientific_name,
        genus,
        family,
        diameter_breast_height,
        year_planted,
        date_planted,
        age_description,
        useful_life_expectency,
        useful_life_expectency_value,
        located_in,
        uploaddate,
        latitude,
        longitude
    FROM Table12_UrbanForestTable
    WHERE com_id = %s
"""




def test_database_connection() -> Dict[str, Any]:
    """Test database connection and whether table exists"""
    try:
        # Test basic connection
        conn = get_connection()
        print("✅ Database connection successful")
        
        # Check if table exists
        table_check_sql = "SHOW TABLES LIKE 'Table12_UrbanForestTable'"
        tables = fetch_all(table_check_sql)
        print(f"🔍 Table check result: {tables}")
        
        if not tables:
            return {"success": False, "error": "Table12_UrbanForestTable not found"}
        
        # Check data count in table
        count_sql = "SELECT COUNT(*) as total FROM Table12_UrbanForestTable"
        count_result = fetch_one(count_sql)
        total_count = count_result.get('total', 0) if count_result else 0
        print(f"📊 Total records in table: {total_count}")
        
        # Check records with coordinates
        coord_count_sql = """
        SELECT COUNT(*) as coord_count 
        FROM Table12_UrbanForestTable 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        coord_result = fetch_one(coord_count_sql)
        coord_count = coord_result.get('coord_count', 0) if coord_result else 0
        print(f"📍 Records with coordinates: {coord_count}")
        
        # Get some sample data
        sample_sql = """
        SELECT com_id, common_name, latitude, longitude 
        FROM Table12_UrbanForestTable 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL 
        LIMIT 5
        """
        sample_data = fetch_all(sample_sql)
        print(f"🔍 Sample data: {sample_data}")
        
        return {
            "success": True,
            "total_records": total_count,
            "coord_records": coord_count,
            "sample_data": sample_data
        }
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return {"success": False, "error": str(e)}


def search_trees(lat: float, lon: float, radius: float, search_keyword: Optional[str] = None) -> Dict[str, Any]:
    """Search trees within specified radius"""
    print(f"🔍 Search parameters: lat={lat}, lon={lon}, radius={radius}, search='{search_keyword}'")
    
    # Calculate bounding box (rough filtering)
    lat_delta = radius / 111320.0  # 1 degree latitude ≈ 111.32km
    lon_delta = radius / (111320.0 * math.cos(math.radians(lat)))  # 1 degree longitude varies with latitude
    
    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lon = lon - lon_delta
    max_lon = lon + lon_delta
    
    print(f"📦 Bounding box: lat=[{min_lat:.6f}, {max_lat:.6f}], lon=[{min_lon:.6f}, {max_lon:.6f}]")
    
    # Debug: print SQL query and parameters
    print(f"🔍 SQL query: {TREE_SEARCH_SQL}")
    print(f"🔍 Query parameters: min_lat={min_lat}, max_lat={max_lat}, min_lon={min_lon}, max_lon={max_lon}")
    
    # Execute SQL query
    try:
        rows = fetch_all(TREE_SEARCH_SQL, (min_lat, max_lat, min_lon, max_lon))
        print(f"🗃️ Database returned {len(rows)} records")
        
        # Debug: print first few records
        if rows:
            print(f"🔍 First 3 record examples:")
            for i, row in enumerate(rows[:3]):
                print(f"  Record {i+1}: {row}")
        else:
            print("❌ Database query returned empty results")
            
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        return {
            "success": False,
            "error": f"Database query failed: {str(e)}",
            "trees": [],
            "total": 0
        }
    
    trees = []
    for row in rows:
        tree_lat = float(row.get('latitude', 0))
        tree_lon = float(row.get('longitude', 0))
        
        # Calculate exact distance
        distance = haversine_distance(lat, lon, tree_lat, tree_lon)
        
        if distance <= radius:
            # Handle search keyword filtering
            if search_keyword and search_keyword.strip():
                search_text = f"{row.get('com_id', '')} {row.get('common_name', '')} {row.get('scientific_name', '')} {row.get('genus', '')} {row.get('family', '')} {row.get('located_in', '')}".lower()
                if search_keyword.lower().strip() not in search_text:
                    continue
            
            # Build tree object
            tree = {
                "com_id": str(row.get('com_id', '')),
                "common_name": row.get('common_name', ''),
                "scientific_name": row.get('scientific_name', ''),
                "genus": row.get('genus', ''),
                "family": row.get('family', ''),
                "latitude": tree_lat,
                "longitude": tree_lon,
                "diameter_breast_height": row.get('diameter_breast_height'),
                "year_planted": row.get('year_planted'),
                "date_planted": _serialize_date(row.get('date_planted')),
                "age_description": row.get('age_description'),
                "maturity_std": normalize_maturity(row.get('age_description')),
                "useful_life_expectency": row.get('useful_life_expectency'),
                "useful_life_expectency_value": row.get('useful_life_expectency_value'),
                "located_in": row.get('located_in'),
                "distance": round(distance, 1),
                "age": calculate_age(row.get('year_planted'))
            }
            trees.append(tree)
    
    # Sort by distance
    trees.sort(key=lambda x: x['distance'])
    
    # Handle duplicate positions
    trees = jitter_duplicates(trees)
    
    print(f"✅ Finally returning {len(trees)} trees")
    if trees:
        print(f"📍 Nearest tree: {trees[0]['common_name']} (distance: {trees[0]['distance']}m)")
    
    return {
        "success": True,
        "trees": trees,
        "total": len(trees),
        "center": {
            "lat": lat,
            "lon": lon,
            "radius": radius
        }
    }


def get_tree_detail(com_id: str) -> Dict[str, Any]:
    """Get detailed information of a single tree"""
    # Execute SQL query
    row = fetch_one(TREE_DETAIL_SQL, (com_id,))
    
    if not row:
        return {
            "success": False,
            "error": "Tree not found"
        }
    
    # Build tree detail object
    tree_detail = {
        "com_id": str(row.get('com_id', '')),
        "common_name": row.get('common_name', ''),
        "scientific_name": row.get('scientific_name', ''),
        "genus": row.get('genus', ''),
        "family": row.get('family', ''),
        "latitude": float(row.get('latitude', 0)) if row.get('latitude') else None,
        "longitude": float(row.get('longitude', 0)) if row.get('longitude') else None,
        "diameter_breast_height": row.get('diameter_breast_height'),
        "year_planted": row.get('year_planted'),
        "date_planted": _serialize_date(row.get('date_planted')),
        "age_description": row.get('age_description'),
        "maturity_std": normalize_maturity(row.get('age_description')),
        "useful_life_expectency": row.get('useful_life_expectency'),
        "useful_life_expectency_value": row.get('useful_life_expectency_value'),
        "located_in": row.get('located_in'),
        "uploaddate": _serialize_date(row.get('uploaddate')),
        "age": calculate_age(row.get('year_planted'))
    }
    
    return {
        "success": True,
        "tree": tree_detail
    }



# ---------- Lambda entry ----------

def handler(event, context):
    method, path, qs, body = _extract_req(event)

    if method == "OPTIONS":
        return _resp(200, {"ok": True})

    try:
        # Debug information
        print(f"Method: {method}, Path: {path}")
        
        # Tree search API - POST method
        if method == "POST" and (path == "/trees/search" or path == "/test/TreeLocator" or path == "/TreeLocator"):
            # Debug: print received request body
            print(f"🔍 Received request body: {body}")
            print(f"🔍 Request body type: {type(body)}")
            print(f"🔍 Request body keys: {list(body.keys()) if isinstance(body, dict) else 'Not a dict'}")
            
            # Check required parameters
            if "lat" not in body or "lon" not in body:
                print("❌ Missing required parameters: lat and lon")
                print(f"❌ Current body content: {body}")
                return _resp(400, {"success": False, "error": "Missing required parameters: lat and lon"})
            
            lat = _to_float(body.get("lat"), None)
            lon = _to_float(body.get("lon"), None)
            radius = _to_float(body.get("radius"), 100)
            search = body.get("search", "").strip() or None
            
            # Debug: print parsed parameters
            print(f"📍 Parsed parameters: lat={lat}, lon={lon}, radius={radius}, search='{search}'")
            
            # Validate coordinates
            if lat is None or lon is None:
                return _resp(400, {"success": False, "error": "Invalid coordinate values: lat and lon must be valid numbers"})
            
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return _resp(400, {"success": False, "error": "Invalid coordinates: lat must be between -90 and 90, lon must be between -180 and 180"})
            
            if radius <= 0 or radius > 5000:
                return _resp(400, {"success": False, "error": "Radius must be between 1 and 5000 meters"})
            
            data = search_trees(lat, lon, radius, search)
            return _resp(200, data)
        
        # Tree details API - GET method, unified use of /test/TreeLocator
        elif method == "GET" and (path == "/test/TreeLocator" or path == "/TreeLocator"):
            # Get com_id from query parameters
            com_id = qs.get("com_id") or qs.get("id") or qs.get("tree_id")
            
            if not com_id:
                return _resp(400, {"success": False, "error": "Missing tree ID parameter (com_id, id, or tree_id)"})
            
            data = get_tree_detail(com_id)
            if data["success"]:
                return _resp(200, data)
            else:
                return _resp(404, data)
        
        # Database test API
        elif method == "GET" and path == "/test/database":
            data = test_database_connection()
            return _resp(200, data)
        
        # Compatible with other path formats for tree details API
        elif method == "GET" and (path.startswith("/trees/") or path.startswith("/test/trees/") or path.startswith("/TreeDetail/")):
            # Extract com_id
            com_id = None
            if path.startswith("/trees/"):
                com_id = path.split("/trees/")[1]
            elif path.startswith("/test/trees/"):
                com_id = path.split("/test/trees/")[1]
            elif path.startswith("/TreeDetail/"):
                com_id = path.split("/TreeDetail/")[1]
            
            # Also support query parameter method
            if not com_id:
                com_id = qs.get("com_id") or qs.get("id")
            
            if not com_id:
                return _resp(400, {"success": False, "error": "Missing tree ID"})
            
            data = get_tree_detail(com_id)
            if data["success"]:
                return _resp(200, data)
            else:
                return _resp(404, data)
        
        
        
        else:
            return _resp(404, {"message": "Not found"})
            
    except Exception as e:
        # Return lightweight error (avoid leaking internals)
        return _resp(500, {"message": f"internal error: {e}"})

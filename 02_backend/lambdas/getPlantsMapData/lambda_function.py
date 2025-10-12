from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from common import fetch_all, fetch_one

# ---------- HTTP helpers (reuse) ----------
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

def _to_float(s: Optional[str], default: float) -> float:
    try:
        return float(s) if s is not None else default
    except Exception:
        return default

# ---------- Map data query SQL ----------
PLANTS_MAP_DATA_SQL = """
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
        RegionCentroidLongitude,
        coords
    FROM Table16_TSX_SpeciesMonitoringTable 
    WHERE EPBCStatus IS NOT NULL 
      AND EPBCStatus != ''
      AND RegionCentroidLatitude IS NOT NULL
      AND RegionCentroidLongitude IS NOT NULL
"""

# State boundary data query SQL
STATE_BOUNDARIES_SQL = """
    SELECT 
        state,
        ST_AsGeoJSON(geometry) as geometry
    FROM Table15_StateShapeTable
    WHERE state IS NOT NULL
"""

def get_plants_map_data(
    state: Optional[str] = None,
    bounds: Optional[str] = None
) -> Dict[str, Any]:
    """Get plant map distribution data"""
    # Build query conditions
    conditions = []
    params = []
    
    if state and state != "All states":
        conditions.append("State = %s")
        params.append(state)
    
    # Handle map boundary filtering
    bounds_condition = ""
    if bounds:
        try:
            # Parse boundary box format: "sw_lat,sw_lng,ne_lat,ne_lng"
            bounds_parts = bounds.split(",")
            if len(bounds_parts) == 4:
                sw_lat, sw_lng, ne_lat, ne_lng = map(float, bounds_parts)
                
                # Use spatial query to filter plants within boundary box
                bounds_condition = """
                AND ST_Within(
                    coords, 
                    ST_MakeEnvelope(%s, %s, %s, %s, 4326)
                )
                """
                params.extend([sw_lng, sw_lat, ne_lng, ne_lat])
        except Exception as e:
            print(f"Boundary parameter parsing error: {e}")
    
    # Build complete SQL
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    sql = PLANTS_MAP_DATA_SQL + f" AND {where_clause}" + bounds_condition
    
    try:
        # Get plant data
        rows = fetch_all(sql, params)
        
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
                "latitude": float(row.get('RegionCentroidLatitude', 0)),
                "longitude": float(row.get('RegionCentroidLongitude', 0)),
                # Prepare data for map markers
                "markerColor": _get_status_color(row.get('EPBCStatus', '')),
                "popupContent": f"""
                    <strong>{row.get('Binomial', '')}</strong><br/>
                    Status: {row.get('EPBCStatus', '')}<br/>
                    Region: {row.get('Region', '')}
                """
            }
            plants.append(plant)
        
        return {
            "success": True,
            "plants": plants,
            "total": len(plants),
            "filters": {
                "state": state,
                "bounds": bounds
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Map data query failed: {str(e)}",
            "plants": [],
            "total": 0
        }

def get_state_boundaries(state: Optional[str] = None) -> Dict[str, Any]:
    """Get state boundary data (GeoJSON format)"""
    conditions = []
    params = []
    
    if state and state != "All states":
        conditions.append("state = %s")
        params.append(state)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    sql = STATE_BOUNDARIES_SQL + f" AND {where_clause}"
    
    try:
        rows = fetch_all(sql, params)
        
        # Build GeoJSON format boundary data
        boundaries = []
        for row in rows:
            state_name = row.get('state', '')
            geometry_json = row.get('geometry', '{}')
            
            try:
                geometry = json.loads(geometry_json)
            except:
                geometry = {}
            
            boundary = {
                "type": "Feature",
                "properties": {
                    "state": state_name,
                    "name": state_name
                },
                "geometry": geometry
            }
            boundaries.append(boundary)
        
        geojson = {
            "type": "FeatureCollection",
            "features": boundaries
        }
        
        return {
            "success": True,
            "boundaries": geojson,
            "total": len(boundaries)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"State boundary data query failed: {str(e)}",
            "boundaries": {"type": "FeatureCollection", "features": []},
            "total": 0
        }

def _get_status_color(status: str) -> str:
    """Return marker color based on conservation status"""
    status = status.lower()
    if 'critically endangered' in status:
        return '#ff0000'  # Red - Critically Endangered
    elif 'endangered' in status:
        return '#ff6b00'   # Orange - Endangered
    elif 'vulnerable' in status:
        return '#ffd700'   # Yellow - Vulnerable
    else:
        return '#808080'   # Gray - Other

# ---------- Lambda main entry point ----------

def lambda_handler(event, context):
    # Extract query parameters
    query_params = _extract_query_params(event)
    
    # Get path information
    path = event.get('path', '')
    
    # Print debug information
    print(f"Received path: {path}")
    print(f"Event: {json.dumps(event, default=str)}")
    
    try:
        # Plant map data endpoint
        if (path == "/plants/map-data" or 
            path == "/api/plants/map-data" or 
            path == "/plantx/getPlantsList/getPlantsMapData/plants/map-data" or
            path.endswith("/plants/map-data")):
            state = query_params.get("state")
            bounds = query_params.get("bounds")
            
            data = get_plants_map_data(state, bounds)
            return _resp(200, data)
        
        # State boundary data endpoint
        elif (path == "/states/boundaries" or 
              path == "/api/states/boundaries" or 
              path == "/plantx/getPlantsList/getPlantsMapData/states/boundaries" or
              path.endswith("/states/boundaries")):
            state = query_params.get("state")
            
            data = get_state_boundaries(state)
            return _resp(200, data)
        
        # Combined endpoint: return both plant data and state boundaries
        elif (path == "/map/data" or 
              path == "/api/map/data" or 
              path == "/plantx/getPlantsList/getPlantsMapData/map/data" or
              path.endswith("/map/data")):
            state = query_params.get("state")
            bounds = query_params.get("bounds")
            
            plants_data = get_plants_map_data(state, bounds)
            boundaries_data = get_state_boundaries(state)
            
            combined_data = {
                "success": plants_data["success"] and boundaries_data["success"],
                "plants": plants_data.get("plants", []),
                "boundaries": boundaries_data.get("boundaries", {}),
                "totalPlants": plants_data.get("total", 0),
                "totalBoundaries": boundaries_data.get("total", 0)
            }
            
            return _resp(200, combined_data)
        
        # Default endpoint: return plant map data when accessing base path directly
        elif (path == "/plantx/getPlantsList/getPlantsMapData" or 
              path == "/plantx/getPlantsList/getPlantsMapData/" or
              path.endswith("/getPlantsMapData") or
              path.endswith("/getPlantsMapData/")):
            state = query_params.get("state")
            bounds = query_params.get("bounds")
            
            data = get_plants_map_data(state, bounds)
            return _resp(200, data)
        
        else:
            return _resp(404, {"success": False, "message": f"Endpoint does not exist, current path: {path}"})
            
    except Exception as e:
        return _resp(500, {"success": False, "message": f"Internal error: {e}"})
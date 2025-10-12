from __future__ import annotations
import json
import urllib.request
from typing import Any, Dict, Optional
from common import fetch_one, fetch_all

# ---------- HTTP helpers (reuse previous code) ----------
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

def _extract_path_parameters(event: Dict[str, Any]) -> Dict[str, str]:
    """Extract path parameters"""
    return event.get("pathParameters") or {}

def _extract_query_params(event: Dict[str, Any]) -> Dict[str, str]:
    """Extract query parameters"""
    return event.get("queryStringParameters") or {}

# ---------- Plant detail query SQL ----------
PLANT_DETAIL_SQL = """
    SELECT 
        ID,
        Binomial,
        CommonName,
        FamilyCommonName,
        Class,
        `Order`,
        Family,
        Genus,
        Species,
        Subspecies,
        FunctionalGroup,
        EPBCStatus,
        IUCNStatus,
        MaxStatus,
        NationalPriorityTaxa,
        State,
        Region,
        RegionCentroidLatitude,
        RegionCentroidLongitude,
        coords
    FROM Table16_TSX_SpeciesMonitoringTable 
    WHERE ID = %s
"""

# Related plants query SQL (plants from same genus or region)
RELATED_PLANTS_SQL = """
    SELECT 
        ID,
        Binomial,
        CommonName,
        EPBCStatus,
        State,
        Region,
        RegionCentroidLatitude,
        RegionCentroidLongitude
    FROM Table16_TSX_SpeciesMonitoringTable 
    WHERE (Genus = %s OR Region = %s OR State = %s)
      AND ID != %s
      AND EPBCStatus IS NOT NULL 
      AND EPBCStatus != ''
    LIMIT 10
"""

# State boundary API endpoint (replace with actual API URL)
STATE_BOUNDARY_API_URL = "https://api.example.com/boundaries/{state}"

def get_state_boundary_from_api(state: str) -> Optional[Dict]:
    """Get state boundary data from external API"""
    if not state:
        return None
        
    try:
        # Build API request URL
        url = STATE_BOUNDARY_API_URL.format(state=state)
        
        # Send HTTP request
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            boundary_data = json.loads(data)
            
            # Adjust based on actual API response structure
            # Assume API returns GeoJSON format
            return boundary_data
            
    except Exception as e:
        print(f"❌ Failed to get state boundary from API: {e}")
        return None

def get_plant_detail(ID: int) -> Dict[str, Any]:
    """Get plant detailed information"""
    print(f"🔍 Querying plant details, ID: {ID}")
    
    try:
        # Get plant basic information
        plant_row = fetch_one(PLANT_DETAIL_SQL, (ID,))
        
        if not plant_row:
            return {
                "success": False,
                "error": f"Plant ID {ID} does not exist"
            }
        
        # Process binary coordinate data
        coords_data = plant_row.get('coords', '')
        if isinstance(coords_data, bytes):
            try:
                # Try WKT format decoding
                coords_str = coords_data.decode('utf-8')
            except UnicodeDecodeError:
                coords_str = ""
        else:
            coords_str = coords_data
        
        # Build plant detail object
        plant_detail = {
            "id": plant_row.get('ID'),
            "taxonomy": {
                "binomial": plant_row.get('Binomial', ''),
                "commonName": plant_row.get('CommonName', ''),
                "familyCommonName": plant_row.get('FamilyCommonName', ''),
                "class": plant_row.get('Class', ''),
                "order": plant_row.get('Order', ''),
                "family": plant_row.get('Family', ''),
                "genus": plant_row.get('Genus', ''),
                "species": plant_row.get('Species', ''),
                "subspecies": plant_row.get('Subspecies', ''),
                "functionalGroup": plant_row.get('FunctionalGroup', '')
            },
            "conservation": {
                "epbcStatus": plant_row.get('EPBCStatus', ''),
                "iucnStatus": plant_row.get('IUCNStatus', ''),
                "maxStatus": plant_row.get('MaxStatus', ''),
                "nationalPriorityTaxa": plant_row.get('NationalPriorityTaxa', ''),
                "statusColor": _get_status_color(plant_row.get('EPBCStatus', ''))
            },
            "location": {
                "state": plant_row.get('State', ''),
                "region": plant_row.get('Region', ''),
                "latitude": float(plant_row.get('RegionCentroidLatitude', 0)) if plant_row.get('RegionCentroidLatitude') else None,
                "longitude": float(plant_row.get('RegionCentroidLongitude', 0)) if plant_row.get('RegionCentroidLongitude') else None,
                "coordinates": coords_str  # Use decoded string
            },
            "displayInfo": {
                "title": plant_row.get('Binomial', ''),
                "subtitle": plant_row.get('CommonName', ''),
                "statusBadge": plant_row.get('EPBCStatus', ''),
                "regionBadge": plant_row.get('Region', ''),
                "stateBadge": plant_row.get('State', '')
            }
        }
        
        # Get related plants
        genus = plant_row.get('Genus', '')
        region = plant_row.get('Region', '')
        state = plant_row.get('State', '')
        
        related_plants = []
        if genus or region or state:
            related_rows = fetch_all(RELATED_PLANTS_SQL, (genus, region, state, ID))
            for row in related_rows:
                related_plant = {
                    "id": row.get('ID'),
                    "binomial": row.get('Binomial', ''),
                    "commonName": row.get('CommonName', ''),
                    "epbcStatus": row.get('EPBCStatus', ''),
                    "state": row.get('State', ''),
                    "region": row.get('Region', ''),
                    "latitude": float(row.get('RegionCentroidLatitude', 0)) if row.get('RegionCentroidLatitude') else None,
                    "longitude": float(row.get('RegionCentroidLongitude', 0)) if row.get('RegionCentroidLongitude') else None,
                    "statusColor": _get_status_color(row.get('EPBCStatus', ''))
                }
                related_plants.append(related_plant)
        
        plant_detail["relatedPlants"] = related_plants
        
        # Get state boundary data (via API call)
        state_boundary = None
        if state:
            state_boundary = get_state_boundary_from_api(state)
        
        plant_detail["stateBoundary"] = state_boundary
        
        # Generate image URLs (based on prototype examples)
        plant_detail["images"] = [
            f"/images/plants/{ID}/main.jpg",
            f"/images/plants/{ID}/habitat.jpg",
            f"/images/plants/{ID}/detail.jpg"
        ]
        
        # Generate description text (based on existing fields)
        plant_detail["description"] = _generate_plant_description(plant_row)
        
        return {
            "success": True,
            "plant": plant_detail
        }
        
    except Exception as e:
        print(f"❌ Plant detail query failed: {e}")
        return {
            "success": False,
            "error": f"Database query failed: {str(e)}"
        }

def _get_status_color(status: str) -> str:
    """Return color based on conservation status"""
    status_lower = status.lower()
    if 'critically endangered' in status_lower:
        return '#ff0000'  # Red - Critically Endangered
    elif 'endangered' in status_lower:
        return '#ff6b00'   # Orange - Endangered
    elif 'vulnerable' in status_lower:
        return '#ffd700'   # Yellow - Vulnerable
    else:
        return '#808080'   # Gray - Other

def _generate_plant_description(plant_row: Dict) -> str:
    """Generate description text based on plant information"""
    binomial = plant_row.get('Binomial', '')
    common_name = plant_row.get('CommonName', '')
    family = plant_row.get('Family', '')
    functional_group = plant_row.get('FunctionalGroup', '')
    state = plant_row.get('State', '')
    region = plant_row.get('Region', '')
    status = plant_row.get('EPBCStatus', '')
    
    description_parts = []
    
    if common_name:
        description_parts.append(f"{common_name} ({binomial})")
    else:
        description_parts.append(binomial)
    
    if family:
        description_parts.append(f"belongs to {family} family")
    
    if functional_group:
        description_parts.append(f"functional group is {functional_group}")
    
    if status:
        description_parts.append(f"conservation status is {status}")
    
    if state and region:
        description_parts.append(f"mainly distributed in {region} region of {state} state")
    elif state:
        description_parts.append(f"distributed in {state} state")
    
    return "。".join(description_parts) + "。"

# ---------- Lambda main entry point ----------

def lambda_handler(event, context):
    # Extract path parameters and query parameters
    path_params = _extract_path_parameters(event)
    query_params = _extract_query_params(event)
    
    # Get path
    path = event.get('path', '')
    
    try:
        # Plant detail API - supports multiple path formats
        # 1. Path parameter method: /plants/{plantId} or /api/plants/{plantId}
        # 2. Query parameter method: /getPlantDetail?plantId=xxx
        plant_id_str = None
        
        # First try to get from path parameters
        if path.startswith("/plants/") or path.startswith("/api/plants/"):
            plant_id_str = path_params.get('plantId', '')
        # Then try to get from query parameters
        elif path.endswith("/getPlantDetail") or "/getPlantDetail" in path:
            plant_id_str = query_params.get('plantId', '')
        
        # If plantId not found in both ways
        if not plant_id_str:
            return _resp(400, {
                "success": False,
                "message": "Missing plant ID parameter, please use path parameter {plantId} or query parameter ?plantId=xxx"
            })
        
        try:
            ID = int(plant_id_str)
        except ValueError:
            return _resp(400, {
                "success": False,
                "message": "Plant ID must be an integer"
            })
        
        data = get_plant_detail(ID)
        if data["success"]:
            return _resp(200, data)
        else:
            return _resp(404, data)
        
        # Other API endpoint handling...
            
    except Exception as e:
        print(f"❌ Lambda execution error: {e}")
        return _resp(500, {
            "success": False,
            "message": f"Internal error: {e}"
        })
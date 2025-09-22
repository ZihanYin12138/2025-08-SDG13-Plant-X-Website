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
    """提取请求方法、路径、查询参数和请求体"""
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
    
    # 调试：打印原始请求体
    print(f"🔍 原始请求体 (类型: {type(body)}): {body}")
    
    # 检查是否需要Base64解码
    is_base64_encoded = event.get("isBase64Encoded", False)
    print(f"🔍 isBase64Encoded: {is_base64_encoded}")
    
    # 处理请求体
    if is_base64_encoded and body:
        try:
            # Base64解码
            decoded_body = base64.b64decode(body).decode('utf-8')
            print(f"🔍 Base64解码后: {decoded_body}")
            body = decoded_body
        except Exception as e:
            print(f"❌ Base64解码失败: {e}")
    
    # 解析JSON请求体
    try:
        parsed_body = json.loads(body) if body else {}
        print(f"✅ JSON解析成功: {parsed_body}")
    except Exception as e:
        print(f"❌ JSON解析失败: {e}")
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
    """序列化日期对象为字符串"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj

# ---------- 地理空间计算函数 ----------

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点间的距离（米）"""
    R = 6371000  # 地球半径（米）
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def normalize_maturity(age_description: Optional[str]) -> str:
    """标准化成熟度描述"""
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
    """计算树木年龄"""
    if not year_planted or year_planted < 1500 or year_planted > reference_year:
        return None
    return reference_year - year_planted

def jitter_duplicates(trees: List[Dict[str, Any]], step: float = 0.00002) -> List[Dict[str, Any]]:
    """为相同坐标的树木添加小偏移量，避免标记重叠"""
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
            # 添加偏移量
            direction = k % 4
            ring = (k // 4) + 1
            offset = ring * step
            
            new_tree = tree.copy()
            if direction == 0:  # 东
                new_tree['longitude'] = lon + offset
            elif direction == 1:  # 西
                new_tree['longitude'] = lon - offset
            elif direction == 2:  # 北
                new_tree['latitude'] = lat + offset
            else:  # 南
                new_tree['latitude'] = lat - offset
            
            result.append(new_tree)
    
    return result


# ---------- 树木搜索SQL ----------
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

# ---------- 树木详情SQL ----------
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
    """测试数据库连接和表是否存在"""
    try:
        # 测试基本连接
        conn = get_connection()
        print("✅ 数据库连接成功")
        
        # 检查表是否存在
        table_check_sql = "SHOW TABLES LIKE 'Table12_UrbanForestTable'"
        tables = fetch_all(table_check_sql)
        print(f"🔍 表检查结果: {tables}")
        
        if not tables:
            return {"success": False, "error": "Table12_UrbanForestTable not found"}
        
        # 检查表中的数据量
        count_sql = "SELECT COUNT(*) as total FROM Table12_UrbanForestTable"
        count_result = fetch_one(count_sql)
        total_count = count_result.get('total', 0) if count_result else 0
        print(f"📊 表中总记录数: {total_count}")
        
        # 检查有坐标的记录数
        coord_count_sql = """
        SELECT COUNT(*) as coord_count 
        FROM Table12_UrbanForestTable 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        coord_result = fetch_one(coord_count_sql)
        coord_count = coord_result.get('coord_count', 0) if coord_result else 0
        print(f"📍 有坐标的记录数: {coord_count}")
        
        # 获取一些示例数据
        sample_sql = """
        SELECT com_id, common_name, latitude, longitude 
        FROM Table12_UrbanForestTable 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL 
        LIMIT 5
        """
        sample_data = fetch_all(sample_sql)
        print(f"🔍 示例数据: {sample_data}")
        
        return {
            "success": True,
            "total_records": total_count,
            "coord_records": coord_count,
            "sample_data": sample_data
        }
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return {"success": False, "error": str(e)}


def search_trees(lat: float, lon: float, radius: float, search_keyword: Optional[str] = None) -> Dict[str, Any]:
    """搜索指定半径内的树木"""
    print(f"🔍 搜索参数: lat={lat}, lon={lon}, radius={radius}, search='{search_keyword}'")
    
    # 计算边界框（粗略筛选）
    lat_delta = radius / 111320.0  # 纬度1度约111.32km
    lon_delta = radius / (111320.0 * math.cos(math.radians(lat)))  # 经度1度随纬度变化
    
    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lon = lon - lon_delta
    max_lon = lon + lon_delta
    
    print(f"📦 边界框: lat=[{min_lat:.6f}, {max_lat:.6f}], lon=[{min_lon:.6f}, {max_lon:.6f}]")
    
    # 调试：打印SQL查询和参数
    print(f"🔍 SQL查询: {TREE_SEARCH_SQL}")
    print(f"🔍 查询参数: min_lat={min_lat}, max_lat={max_lat}, min_lon={min_lon}, max_lon={max_lon}")
    
    # 执行SQL查询
    try:
        rows = fetch_all(TREE_SEARCH_SQL, (min_lat, max_lat, min_lon, max_lon))
        print(f"🗃️ 数据库返回 {len(rows)} 条记录")
        
        # 调试：打印前几条记录
        if rows:
            print(f"🔍 前3条记录示例:")
            for i, row in enumerate(rows[:3]):
                print(f"  记录{i+1}: {row}")
        else:
            print("❌ 数据库查询返回空结果")
            
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
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
        
        # 精确计算距离
        distance = haversine_distance(lat, lon, tree_lat, tree_lon)
        
        if distance <= radius:
            # 处理搜索关键词筛选
            if search_keyword and search_keyword.strip():
                search_text = f"{row.get('com_id', '')} {row.get('common_name', '')} {row.get('scientific_name', '')} {row.get('genus', '')} {row.get('family', '')} {row.get('located_in', '')}".lower()
                if search_keyword.lower().strip() not in search_text:
                    continue
            
            # 构建树木对象
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
    
    # 按距离排序
    trees.sort(key=lambda x: x['distance'])
    
    # 处理重复位置
    trees = jitter_duplicates(trees)
    
    print(f"✅ 最终返回 {len(trees)} 棵树木")
    if trees:
        print(f"📍 最近树木: {trees[0]['common_name']} (距离: {trees[0]['distance']}m)")
    
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
    """获取单棵树木的详细信息"""
    # 执行SQL查询
    row = fetch_one(TREE_DETAIL_SQL, (com_id,))
    
    if not row:
        return {
            "success": False,
            "error": "Tree not found"
        }
    
    # 构建树木详情对象
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
        # 调试信息
        print(f"Method: {method}, Path: {path}")
        
        # 树木搜索API - POST方法
        if method == "POST" and (path == "/trees/search" or path == "/test/TreeLocator" or path == "/TreeLocator"):
            # 调试：打印接收到的请求体
            print(f"🔍 接收到的请求体: {body}")
            print(f"🔍 请求体类型: {type(body)}")
            print(f"🔍 请求体键: {list(body.keys()) if isinstance(body, dict) else 'Not a dict'}")
            
            # 检查必需的参数
            if "lat" not in body or "lon" not in body:
                print("❌ 缺少必需的参数: lat 和 lon")
                print(f"❌ 当前body内容: {body}")
                return _resp(400, {"success": False, "error": "Missing required parameters: lat and lon"})
            
            lat = _to_float(body.get("lat"), None)
            lon = _to_float(body.get("lon"), None)
            radius = _to_float(body.get("radius"), 100)
            search = body.get("search", "").strip() or None
            
            # 调试：打印解析后的参数
            print(f"📍 解析后的参数: lat={lat}, lon={lon}, radius={radius}, search='{search}'")
            
            # 验证坐标是否有效
            if lat is None or lon is None:
                return _resp(400, {"success": False, "error": "Invalid coordinate values: lat and lon must be valid numbers"})
            
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return _resp(400, {"success": False, "error": "Invalid coordinates: lat must be between -90 and 90, lon must be between -180 and 180"})
            
            if radius <= 0 or radius > 5000:
                return _resp(400, {"success": False, "error": "Radius must be between 1 and 5000 meters"})
            
            data = search_trees(lat, lon, radius, search)
            return _resp(200, data)
        
        # 树木详情API - GET方法，统一使用 /test/TreeLocator
        elif method == "GET" and (path == "/test/TreeLocator" or path == "/TreeLocator"):
            # 从查询参数获取 com_id
            com_id = qs.get("com_id") or qs.get("id") or qs.get("tree_id")
            
            if not com_id:
                return _resp(400, {"success": False, "error": "Missing tree ID parameter (com_id, id, or tree_id)"})
            
            data = get_tree_detail(com_id)
            if data["success"]:
                return _resp(200, data)
            else:
                return _resp(404, data)
        
        # 数据库测试API
        elif method == "GET" and path == "/test/database":
            data = test_database_connection()
            return _resp(200, data)
        
        # 兼容其他路径格式的树木详情API
        elif method == "GET" and (path.startswith("/trees/") or path.startswith("/test/trees/") or path.startswith("/TreeDetail/")):
            # 提取 com_id
            com_id = None
            if path.startswith("/trees/"):
                com_id = path.split("/trees/")[1]
            elif path.startswith("/test/trees/"):
                com_id = path.split("/test/trees/")[1]
            elif path.startswith("/TreeDetail/"):
                com_id = path.split("/TreeDetail/")[1]
            
            # 也支持查询参数方式
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

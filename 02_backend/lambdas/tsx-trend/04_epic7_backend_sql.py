# This .py file is a sql version of 03_epic7_backend_local.py
# Name: Zihan

from flask import Flask, jsonify, abort
from flask_cors import CORS
import pandas as pd
import geopandas as gpd
from shapely import wkt
import json
import mysql.connector
from mysql.connector import Error

# --- 初始化 Flask 应用 ---
app = Flask(__name__)
CORS(app) # 允许跨域请求

# --- 1. 更新：在应用启动时从 MySQL 加载数据 ---

# 数据库连接配置
db_config = {
    'host': 'database-plantx.cqz06uycysiz.us-east-1.rds.amazonaws.com',
    'user': 'zihan',
    'password': '2002317Yzh12138.',
    'database': 'FIT5120_PlantX_Database',
    'allow_local_infile': True,
    'use_pure': True,
    'charset': 'utf8mb4'
}

# 先初始化空的 DataFrame，以防数据库连接失败
df_tsx = pd.DataFrame()
gdf_states = gpd.GeoDataFrame()

try:
    print("🔄 Connecting to MySQL database...")
    connection = mysql.connector.connect(**db_config)
    
    if connection.is_connected():
        print("✅ MySQL Connection Successful.")
        
        # 查询 Table14 (时间序列数据)
        query_tsx = "SELECT * FROM Table14_TSX_Table_VIC"
        df_tsx = pd.read_sql(query_tsx, connection)
        print(f"✅ Loaded {len(df_tsx)} rows from Table14_TSX_Table_VIC.")
        
        # 查询 Table15 (地理形状数据)
        # 使用 ST_AsText() 将 MySQL 的 geometry 类型转换为 WKT 文本，以便 GeoPandas 读取
        query_shapes = "SELECT state, ST_AsText(geometry) as geometry FROM Table15_StateShapeTable"
        df_shapes_from_db = pd.read_sql(query_shapes, connection)
        
        # 将 WKT 文本转换回 geometry 对象，并创建 GeoDataFrame
        df_shapes_from_db['geometry'] = df_shapes_from_db['geometry'].apply(wkt.loads)
        gdf_states = gpd.GeoDataFrame(df_shapes_from_db, geometry='geometry')
        print(f"✅ Loaded {len(gdf_states)} state shapes from Table15_StateShapeTable.")

except Error as e:
    print(f"❌ Error while connecting to MySQL or fetching data: {e}")

finally:
    # 加载完数据后，及时关闭连接
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("🚪 MySQL connection closed.")


# --- 2. API Endpoints (这部分代码无需任何修改) ---

@app.route('/api/map/geojson', methods=['GET'])
def get_map_base_geojson_endpoint():
    if gdf_states.empty:
        abort(500, description="GeoJSON data not loaded on the server. Check database connection.")
    return jsonify(json.loads(gdf_states.to_json()))

@app.route('/api/map/data/<int:year>', methods=['GET'])
def get_choropleth_data_for_year_endpoint(year):
    if df_tsx.empty:
        abort(500, description="TSX data not loaded on the server. Check database connection.")
    if year not in df_tsx['year'].unique():
        abort(404, description=f"Year {year} not found in the dataset.")
    data_for_year = df_tsx[df_tsx['year'] == year]
    result = pd.Series(data_for_year.index_value.values, index=data_for_year.state).to_dict()
    return jsonify(result)

@app.route('/api/chart/data/<string:state>', methods=['GET'])
def get_state_timeseries_data_endpoint(state):
    if df_tsx.empty:
        abort(500, description="TSX data not loaded on the server. Check database connection.")
    if state not in df_tsx['state'].unique():
        abort(404, description=f"State '{state}' not found in the dataset.")
    state_data = df_tsx[df_tsx['state'] == state]
    result = json.loads(state_data.to_json(orient='records'))
    return jsonify(result)

# --- 3. 运行服务器 (生产环境优化) ---
if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
    
    
    
# python .\04_epic7_backend_sql.py

# 1. 测试 GeoJSON 接口 (获取地图边界)
# 访问: http://127.0.0.1:5000/api/map/geojson
# 你应该会看到满屏的文本，以 {"features": [{"geometry": ... 开头。这就是地图的 GeoJSON 数据。

# 2. 测试年份数据接口 (获取2022年的地图颜色数据)
# 访问: http://127.0.0.1:5000/api/map/data/2022
# 你应该会看到一个简洁的 JSON 对象，类似 {"Australian Capital Territory": 1.13, "National": 0.36, ...}。

# 3. 测试州时间序列接口 (获取新南威尔士州的折线图数据)
# 访问: http://127.0.0.1:5000/api/chart/data/New South Wales
# 你应该会看到一个包含多条记录的 JSON 数组，[{"year": 2000, "index_value": 1.0, ...}, {"year": 2001, ...}]。
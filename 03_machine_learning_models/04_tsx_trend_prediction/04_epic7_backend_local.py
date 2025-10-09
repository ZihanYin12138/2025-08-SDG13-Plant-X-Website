# This .py file is a .py version of 03_epic7_backend_local.ipynb
# Name: Zihan

from flask import Flask, jsonify, abort
from flask_cors import CORS
import pandas as pd
import geopandas as gpd
from shapely import wkt
import json

# --- 初始化 Flask 应用 ---
app = Flask(__name__)
# CORS(app) 允许来自任何源的请求，这在开发中很方便
CORS(app)

# --- 1. 在应用启动时加载和预处理数据 (只执行一次) ---
# 这样做可以避免每次用户请求都重新读取文件，提高性能
try:
    df_tsx = pd.read_csv('Table14_TSX_Table_VIC_version4.csv')
    df_shapes = pd.read_csv('Table15_StateShapeTable.csv')
    
    # 将 WKT 字符串转换为 geometry 对象
    df_shapes['geometry'] = df_shapes['geometry'].apply(wkt.loads)
    gdf_states = gpd.GeoDataFrame(df_shapes, geometry='geometry')
    
    print("✅ Data loaded and preprocessed successfully.")
except FileNotFoundError as e:
    print(f"❌ Error: {e}. Make sure CSV files are in the same directory as app.py.")
    df_tsx = pd.DataFrame()
    gdf_states = gpd.GeoDataFrame()

# --- 2. 创建 API Endpoints (接口) ---

@app.route('/api/map/geojson', methods=['GET'])
def get_map_base_geojson_endpoint():
    """
    API Endpoint: 提供地图的 GeoJSON 基础层。
    前端访问: http://1227.0.0.1:5000/api/map/geojson
    """
    if gdf_states.empty:
        # 如果数据加载失败，返回服务器错误
        abort(500, description="GeoJSON data not loaded on the server.")
    
    # geopandas 的 .to_json() 返回的是字符串，我们先用 json.loads 转成 Python 字典/列表
    # 再用 jsonify 转换成 Flask 的 Response 对象，这样能确保 HTTP Header 正确
    return jsonify(json.loads(gdf_states.to_json()))

@app.route('/api/map/data/<int:year>', methods=['GET'])
def get_choropleth_data_for_year_endpoint(year):
    """
    API Endpoint: 根据年份获取 Choropleth Map 的数据。
    前端访问示例: http://127.0.0.1:5000/api/map/data/2010
    """
    if df_tsx.empty:
        abort(500, description="TSX data not loaded on the server.")
        
    if year not in df_tsx['year'].unique():
        abort(404, description=f"Year {year} not found in the dataset.")

    data_for_year = df_tsx[df_tsx['year'] == year]
    result = pd.Series(data_for_year.index_value.values, index=data_for_year.state).to_dict()
    return jsonify(result)

@app.route('/api/chart/data/<string:state>', methods=['GET'])
def get_state_timeseries_data_endpoint(state):
    """
    API Endpoint: 根据州名获取折线图的时间序列数据。
    前端访问示例: http://127.0.0.1:5000/api/chart/data/Victoria
    """
    if df_tsx.empty:
        abort(500, description="TSX data not loaded on the server.")

    if state not in df_tsx['state'].unique():
        abort(404, description=f"State '{state}' not found in the dataset.")

    state_data = df_tsx[df_tsx['state'] == state]
    result = json.loads(state_data.to_json(orient='records'))
    return jsonify(result)

# --- 3. 运行服务器 ---
if __name__ == '__main__':
    # debug=True 会让服务器在代码改变后自动重启，方便开发
    app.run(debug=True, port=5000)



# python .\04_epic7_backend_local.py

# 1. 测试 GeoJSON 接口 (获取地图边界)
# 访问: http://127.0.0.1:5000/api/map/geojson
# 你应该会看到满屏的文本，以 {"features": [{"geometry": ... 开头。这就是地图的 GeoJSON 数据。

# 2. 测试年份数据接口 (获取2022年的地图颜色数据)
# 访问: http://127.0.0.1:5000/api/map/data/2022
# 你应该会看到一个简洁的 JSON 对象，类似 {"Australian Capital Territory": 1.13, "National": 0.36, ...}。

# 3. 测试州时间序列接口 (获取新南威尔士州的折线图数据)
# 访问: http://127.0.0.1:5000/api/chart/data/New South Wales
# 你应该会看到一个包含多条记录的 JSON 数组，[{"year": 2000, "index_value": 1.0, ...}, {"year": 2001, ...}]。
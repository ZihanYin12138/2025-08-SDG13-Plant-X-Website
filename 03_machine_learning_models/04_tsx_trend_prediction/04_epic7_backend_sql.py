# This .py file is a SQL version of 03_epic7_backend_local.py
# Name: Zihan

from flask import Flask, jsonify, abort
from flask_cors import CORS
import pandas as pd
import geopandas as gpd
from shapely import wkt
import json
import mysql.connector
from mysql.connector import Error

# --- Initialize Flask Application ---
app = Flask(__name__)
CORS(app) # Allow cross-origin requests

# --- 1. Updated: Load Data from MySQL at App Startup ---

# Database connection configuration
db_config = {
    'host': 'database-plantx.cqz06uycysiz.us-east-1.rds.amazonaws.com',
    'user': 'zihan',
    'password': '2002317Yzh12138.',
    'database': 'FIT5120_PlantX_Database',
    'allow_local_infile': True,
    'use_pure': True,
    'charset': 'utf8mb4'
}

# Initialize empty DataFrames in case of database connection failure
df_tsx = pd.DataFrame()
gdf_states = gpd.GeoDataFrame()

try:
    print("🔄 Connecting to MySQL database...")
    connection = mysql.connector.connect(**db_config)
    
    if connection.is_connected():
        print("✅ MySQL Connection Successful.")
        
        # Query Table14 (time series data)
        query_tsx = "SELECT * FROM Table14_TSX_Table_VIC"
        df_tsx = pd.read_sql(query_tsx, connection)
        print(f"✅ Loaded {len(df_tsx)} rows from Table14_TSX_Table_VIC.")
        
        # Query Table15 (geographic shape data)
        # Use ST_AsText() to convert MySQL geometry type to WKT text for GeoPandas
        query_shapes = "SELECT state, ST_AsText(geometry) as geometry FROM Table15_StateShapeTable"
        df_shapes_from_db = pd.read_sql(query_shapes, connection)
        
        # Convert WKT text back to geometry objects and create GeoDataFrame
        df_shapes_from_db['geometry'] = df_shapes_from_db['geometry'].apply(wkt.loads)
        gdf_states = gpd.GeoDataFrame(df_shapes_from_db, geometry='geometry')
        print(f"✅ Loaded {len(gdf_states)} state shapes from Table15_StateShapeTable.")

except Error as e:
    print(f"❌ Error while connecting to MySQL or fetching data: {e}")

finally:
    # Close connection after loading data
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("🚪 MySQL connection closed.")


# --- 2. API Endpoints (this code requires no modifications) ---

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

# --- 3. Run Server (no modifications needed) ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
    
    
# python .\04_epic7_backend_sql.py



# Instructions for Testing the Backend API

# 1.  **Test GeoJSON Endpoint (Get Map Boundaries)**  
#     Access: http://127.0.0.1:5000/api/map/geojson  
#     You should see a screen full of text starting with `{"features": [{"geometry": ...`. This is the GeoJSON data for the map.

# 2.  **Test Year Data Endpoint (Get Color Data for 2022 Map)**  
#     Access: http://127.0.0.1:5000/api/map/data/2022  
#     You should see a concise JSON object like `{"Australian Capital Territory": 1.13, "National": 0.36, ...}`.

# 3.  **Test State Timeseries Endpoint (Get Line Chart Data for New South Wales)**  
#     Access: http://127.0.0.1:5000/api/chart/data/New South Wales  
#     You should see a JSON array with multiple records: `[{"year": 2000, "index_value": 1.0, ...}, {"year": 2001, ...}]`.
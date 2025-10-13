# This .py file is a .py version of 03_epic7_backend_local.ipynb
# Name: Zihan

from flask import Flask, jsonify, abort
from flask_cors import CORS
import pandas as pd
import geopandas as gpd
from shapely import wkt
import json

# --- Initialize Flask Application ---
app = Flask(__name__)
# CORS(app) allows requests from any origin, convenient during development
CORS(app)

# --- 1. Load and Preprocess Data at App Startup (Executed Once) ---
# This avoids reloading files on every user request, improving performance
try:
    df_tsx = pd.read_csv('Table14_TSX_Table_VIC_version4.csv')
    df_shapes = pd.read_csv('Table15_StateShapeTable.csv')
    
    # Convert WKT strings to geometry objects
    df_shapes['geometry'] = df_shapes['geometry'].apply(wkt.loads)
    gdf_states = gpd.GeoDataFrame(df_shapes, geometry='geometry')
    
    print("✅ Data loaded and preprocessed successfully.")
except FileNotFoundError as e:
    print(f"❌ Error: {e}. Make sure CSV files are in the same directory as app.py.")
    df_tsx = pd.DataFrame()
    gdf_states = gpd.GeoDataFrame()

# --- 2. Create API Endpoints ---

@app.route('/api/map/geojson', methods=['GET'])
def get_map_base_geojson_endpoint():
    """
    API Endpoint: Provides GeoJSON base layer for the map.
    Frontend access: http://127.0.0.1:5000/api/map/geojson
    """
    if gdf_states.empty:
        # Return server error if data loading failed
        abort(500, description="GeoJSON data not loaded on the server.")
    
    # geopandas .to_json() returns string, convert to Python dict/list with json.loads
    # Then use jsonify to ensure proper Flask Response object with correct HTTP Headers
    return jsonify(json.loads(gdf_states.to_json()))

@app.route('/api/map/data/<int:year>', methods=['GET'])
def get_choropleth_data_for_year_endpoint(year):
    """
    API Endpoint: Gets Choropleth Map data for a specific year.
    Frontend example: http://127.0.0.1:5000/api/map/data/2010
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
    API Endpoint: Gets timeseries data for line charts by state name.
    Frontend example: http://127.0.0.1:5000/api/chart/data/Victoria
    """
    if df_tsx.empty:
        abort(500, description="TSX data not loaded on the server.")

    if state not in df_tsx['state'].unique():
        abort(404, description=f"State '{state}' not found in the dataset.")

    state_data = df_tsx[df_tsx['state'] == state]
    result = json.loads(state_data.to_json(orient='records'))
    return jsonify(result)

# --- 3. Run the Server ---
if __name__ == '__main__':
    # debug=True enables auto-restart on code changes during development
    app.run(debug=True, port=5000)



# python .\04_epic7_backend_local.py



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
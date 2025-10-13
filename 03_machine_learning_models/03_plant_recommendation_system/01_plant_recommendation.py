# .py version of 01_plant_recommendation.ipynb
# Name: Zihan

# Plant recommendation system that matches weather conditions with plant requirements
# Uses 16-day weather forecast to determine suitable plants for specific locations
# Supports both human-readable and JSON output formats for different use cases

# Key features:
# - MySQL database integration for plant data
# - Open-Meteo API for weather forecasting
# - Multi-criteria matching logic (temperature, sunlight, watering, drought tolerance)
# - Command-line interface with latitude/longitude parameters
# - Random shuffling of results for variety

# Usage examples:
# python plant_recommendation.py --lat -37.8136 --lon 144.9631
# python plant_recommendation.py --lat -37.8749 --lon 145.0417 --json

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Weather-Based Plant Recommendation Engine

This script fetches a 16-day weather forecast for a given location,
loads plant data from a MySQL database, and recommends suitable plants
based on a set of matching rules.
"""

import requests
import pandas as pd
import numpy as np
import json
import random
import mysql.connector
from mysql.connector import Error
import argparse  # <-- New: for handling command line arguments

# ==============================================================================
# 1. Constants and Configuration
# ==============================================================================

# Database connection configuration
# Note: In production environment, use more secure password management methods like environment variables.
DB_CONFIG = {
    'host': 'database-plantx.cqz06uycysiz.us-east-1.rds.amazonaws.com',
    'user': 'zihan',
    'password': '2002317Yzh12138.',
    'database': 'FIT5120_PlantX_Database',
    'use_pure': True,
    'charset': 'utf8mb4'
}

# Hardiness zone to temperature (°C) conversion table
HARDINESS_ZONE_TO_CELSIUS = {
    "1": -51.1, "2": -45.6, "3": -40.0, "4": -34.4, "5": -28.9,
    "6": -23.3, "7": -17.8, "8": -12.2, "9": -6.7, "10": -1.1,
    "11": 4.4,  "12": 10.0, "13": 15.6
}

# ==============================================================================
# 2. Function Definitions
# ==============================================================================

def load_plants_from_db(config):
    """Load plant data from MySQL database and perform preprocessing."""
    df_plants = pd.DataFrame() # Default: create empty DataFrame
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("--> Successfully connected to MySQL database...")
            query = "SELECT * FROM Table13_GeneralPlantListforRecommendation;"
            df_plants = pd.read_sql(query, connection)
            print(f"--> Successfully loaded {len(df_plants)} plant species from database.")
    except Error as e:
        print(f"!! Error loading data from MySQL: {e}")
        return pd.DataFrame()
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("--> MySQL database connection closed.")

    if not df_plants.empty:
        df_plants['sunlight'] = df_plants['sunlight'].apply(json.loads)
        df_plants['drought_tolerant'] = df_plants['drought_tolerant'].astype(bool)
    
    return df_plants

def get_and_aggregate_weather_data(latitude, longitude):
    """Fetch and aggregate weather data based on latitude and longitude."""
    api_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
        "&daily=precipitation_sum,sunshine_duration,uv_index_max,temperature_2m_max,"
        "temperature_2m_min,relative_humidity_2m_mean&timezone=auto&forecast_days=16"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        weather_data = response.json()['daily']
    except requests.exceptions.RequestException as e:
        print(f"!! API request failed: {e}")
        return None

    def clean_list(data_list):
        return [item for item in data_list if item is not None]

    temp_min_list = clean_list(weather_data['temperature_2m_min'])
    temp_max_list = clean_list(weather_data['temperature_2m_max'])
    sunshine_list = clean_list(weather_data['sunshine_duration'])
    uv_list = clean_list(weather_data['uv_index_max'])
    precipitation_list = clean_list(weather_data['precipitation_sum'])
    humidity_list = clean_list(weather_data['relative_humidity_2m_mean'])
    
    aggregated_weather = {
        'extreme_min_temp': np.min(temp_min_list) if temp_min_list else None,
        'extreme_max_temp': np.max(temp_max_list) if temp_max_list else None,
        'avg_sunshine_duration': (np.mean(sunshine_list) / 3600) if sunshine_list else None,
        'avg_max_uv_index': np.mean(uv_list) if uv_list else None,
        'avg_daily_precipitation': np.mean(precipitation_list) if precipitation_list else None,
        'avg_relative_humidity': np.mean(humidity_list) if humidity_list else None
    }
    
    return {
        key: round(value, 2) if isinstance(value, float) else value
        for key, value in aggregated_weather.items()
    }

def is_plant_suitable(agg_weather, plant_row):
    """Core matching logic: determine if individual plant meets weather conditions."""
    if agg_weather.get('extreme_min_temp') is None: return False # Cannot evaluate if weather data invalid
    
    # Rule 1: Survival baseline
    if agg_weather['extreme_min_temp'] < plant_row['absolute_min_temp_c']:
        return False

    # Rule 2: Sunlight requirements
    sun_duration = agg_weather.get('avg_sunshine_duration', 0)
    uv_index = agg_weather.get('avg_max_uv_index', 0)
    sunlight_needs = plant_row['sunlight']
    sun_duration_ok = False
    if 'full sun' in sunlight_needs and sun_duration >= 6: sun_duration_ok = True
    if ('part shade' in sunlight_needs or 'part sun/part shade' in sunlight_needs) and (3 <= sun_duration < 6): sun_duration_ok = True
    if 'full shade' in sunlight_needs and sun_duration < 3: sun_duration_ok = True
    if not sun_duration_ok: return False
    if uv_index > 8 and sunlight_needs == ['part shade']: return False
    if uv_index < 3 and sunlight_needs == ['full sun']: return False

    # Rule 3: Watering requirements
    precipitation = agg_weather.get('avg_daily_precipitation', 0)
    watering_needs = plant_row['watering']
    if watering_needs == 'Frequent' and precipitation < 3: return False
    if watering_needs == 'Minimal' and precipitation > 5: return False
    if watering_needs == 'Average' and not (1 <= precipitation <= 8): return False

    # Rule 4: Drought tolerance
    humidity = agg_weather.get('avg_relative_humidity', 0)
    if not plant_row['drought_tolerant'] and humidity < 40: return False

    return True

def get_plant_recommendations(latitude, longitude):
    """Main coordination function: execute complete recommendation workflow."""
    print(f"\nGenerating plant recommendation report for coordinates ({latitude}, {longitude})...")
    
    df_plants = load_plants_from_db(DB_CONFIG)
    if df_plants.empty:
        print("!! Cannot load plant data, recommendation process terminated.")
        return None, None
    
    agg_weather = get_and_aggregate_weather_data(latitude, longitude)
    if not agg_weather:
        print("!! Cannot fetch weather data, recommendation process terminated.")
        return None, None
        
    is_suitable_series = df_plants.apply(lambda row: is_plant_suitable(agg_weather, row), axis=1)
    suitable_plant_ids = df_plants[is_suitable_series]['general_plant_id'].tolist()
    random.shuffle(suitable_plant_ids)
    
    return agg_weather, suitable_plant_ids

# ==============================================================================
# 3. Main Execution Block
# ==============================================================================

if __name__ == "__main__":
    # --- Setup command line argument parsing ---
    parser = argparse.ArgumentParser(description="Recommend suitable plants based on 16-day weather forecast.")
    parser.add_argument('--lat', type=float, default=-37.8136, help='Latitude of target location (e.g.: -37.8136)')
    parser.add_argument('--lon', type=float, default=144.9631, help='Longitude of target location (e.g.: 144.9631)')
    # --- Add --json parameter ---
    parser.add_argument('--json', action='store_true', help='Output results in single JSON format for easier program parsing.')
    args = parser.parse_args()

    # --- Call main function and get results ---
    weather_info, plant_ids = get_plant_recommendations(latitude=args.lat, longitude=args.lon)

    # --- Determine output format based on --json parameter ---
    if args.json:
        # If --json flag present, output single JSON object
        if weather_info and plant_ids is not None:
            final_output = {
                "aggregated_weather": weather_info,
                "recommended_plant_ids": plant_ids
            }
            print(json.dumps(final_output, indent=4))
        else:
            # Even if failed, output standard JSON error message
            print(json.dumps({"error": "Failed to generate recommendations."}, indent=4))
    else:
        # Otherwise, output human-readable formatted report
        if weather_info and plant_ids is not None:
            print("\n" + "="*50)
            print("      16-Day Aggregated Weather Information      ")
            print("="*50)
            for key, value in weather_info.items():
                print(f"{key}: {value}")
            
            print("\n" + "="*50)
            print("      Suitable Plant ID List (Randomly Shuffled)      ")
            print("="*50)
            if plant_ids:
                print(plant_ids)
            else:
                print("No particularly suitable plants found based on future weather.")
            print("="*50)
       
# python 01_plant_recommendation.py --lat -36.7570 --lon 144.2794
# python 01_plant_recommendation.py --lat -37.8749 --lon 145.0417 --json
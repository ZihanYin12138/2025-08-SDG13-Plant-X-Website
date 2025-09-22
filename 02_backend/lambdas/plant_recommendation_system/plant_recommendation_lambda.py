# .py version of 01_plant_recommendation.ipynb - Lambda优化版本
# Name: Zihan

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Weather-Based Plant Recommendation Engine - Lambda Optimized Version

This script fetches a 16-day weather forecast for a given location,
loads plant data from a MySQL database, and recommends suitable plants
based on a set of matching rules. Optimized for AWS Lambda without pandas/numpy.
"""

import requests
import json
import random
import os
from common.db_utils import fetch_all

# ==============================================================================
# 1. Constants and Configuration
# ==============================================================================

# Hardiness zone to temperature (°C) conversion table
HARDINESS_ZONE_TO_CELSIUS = {
    "1": -51.1, "2": -45.6, "3": -40.0, "4": -34.4, "5": -28.9,
    "6": -23.3, "7": -17.8, "8": -12.2, "9": -6.7, "10": -1.1,
    "11": 4.4,  "12": 10.0, "13": 15.6
}

# ==============================================================================
# 2. Function Definitions
# ==============================================================================

def load_plants_from_db():
    """Load plant data from MySQL database and perform preprocessing."""
    plants = []  # Use list instead of DataFrame
    try:
        print("--> Connecting to MySQL database...")
        query = "SELECT * FROM Table13_GeneralPlantListforRecommendation;"
        rows = fetch_all(query)
        plants = list(rows)  # Convert to list
        print(f"--> Successfully loaded {len(plants)} plants from database.")
    except Exception as e:
        print(f"!! Error occurred while loading data from MySQL: {e}")
        return []

    # Preprocess data
    for plant in plants:
        if plant.get('sunlight'):
            try:
                plant['sunlight'] = json.loads(plant['sunlight']) if isinstance(plant['sunlight'], str) else plant['sunlight']
            except:
                plant['sunlight'] = []
        if plant.get('drought_tolerant'):
            plant['drought_tolerant'] = bool(plant['drought_tolerant'])
    
    return plants

def get_default_weather_data():
    """Get default weather data (used when API fails)"""
    print("--> Using default weather data")
    return {
        'extreme_min_temp': 5.0,  # Default minimum temperature
        'extreme_max_temp': 25.0,  # Default maximum temperature
        'avg_sunshine_duration': 6.0,  # Default average sunshine
        'avg_max_uv_index': 5.0,  # Default UV index
        'avg_daily_precipitation': 3.0,  # Default precipitation
        'avg_relative_humidity': 60.0  # Default humidity
    }

def get_and_aggregate_weather_data(latitude, longitude):
    """Get and aggregate weather data based on latitude and longitude."""
    api_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
        "&daily=precipitation_sum,sunshine_duration,uv_index_max,temperature_2m_max,"
        "temperature_2m_min,relative_humidity_2m_mean&timezone=auto&forecast_days=16"
    )
    
    # Set timeout and retry
    max_retries = 3
    timeout = 10  # 10 second timeout
    
    weather_data = None
    for attempt in range(max_retries):
        try:
            print(f"--> Attempting to get weather data (attempt {attempt + 1})...")
            response = requests.get(api_url, timeout=timeout)
            response.raise_for_status()
            weather_data = response.json()['daily']
            print(f"--> Weather data retrieved successfully")
            break
        except requests.exceptions.Timeout as e:
            print(f"!! Request timeout (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                print("!! All retries timed out, using default weather data")
                return get_default_weather_data()
        except requests.exceptions.RequestException as e:
            print(f"!! API request failed (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                print("!! All retries failed, using default weather data")
                return get_default_weather_data()
        except Exception as e:
            print(f"!! Unknown error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                print("!! All retries failed, using default weather data")
                return get_default_weather_data()

    # If weather data is successfully retrieved, process it
    if weather_data:
        def clean_list(data_list):
            return [item for item in data_list if item is not None]

        temp_min_list = clean_list(weather_data['temperature_2m_min'])
        temp_max_list = clean_list(weather_data['temperature_2m_max'])
        sunshine_list = clean_list(weather_data['sunshine_duration'])
        uv_list = clean_list(weather_data['uv_index_max'])
        precipitation_list = clean_list(weather_data['precipitation_sum'])
        humidity_list = clean_list(weather_data['relative_humidity_2m_mean'])
        
        # Use pure Python to implement aggregation calculations
        aggregated_weather = {
            'extreme_min_temp': min(temp_min_list) if temp_min_list else None,
            'extreme_max_temp': max(temp_max_list) if temp_max_list else None,
            'avg_sunshine_duration': (sum(sunshine_list) / len(sunshine_list) / 3600) if sunshine_list else None,
            'avg_max_uv_index': sum(uv_list) / len(uv_list) if uv_list else None,
            'avg_daily_precipitation': sum(precipitation_list) / len(precipitation_list) if precipitation_list else None,
            'avg_relative_humidity': sum(humidity_list) / len(humidity_list) if humidity_list else None
        }
        
        return {
            key: round(value, 2) if isinstance(value, float) else value
            for key, value in aggregated_weather.items()
        }
    else:
        # If all retries fail, return default data
        return get_default_weather_data()

def is_plant_suitable(agg_weather, plant):
    """Core matching logic: determine if a single plant meets weather conditions."""
    if agg_weather.get('extreme_min_temp') is None: 
        return False  # If weather data is invalid, cannot determine
    
    # Rule 1: Survival baseline
    if agg_weather['extreme_min_temp'] < plant['absolute_min_temp_c']:
        return False

    # Rule 2: Sunlight requirements
    sun_duration = agg_weather.get('avg_sunshine_duration', 0)
    uv_index = agg_weather.get('avg_max_uv_index', 0)
    sunlight_needs = plant.get('sunlight', [])
    sun_duration_ok = False
    
    if 'full sun' in sunlight_needs and sun_duration >= 6: 
        sun_duration_ok = True
    if ('part shade' in sunlight_needs or 'part sun/part shade' in sunlight_needs) and (3 <= sun_duration < 6): 
        sun_duration_ok = True
    if 'full shade' in sunlight_needs and sun_duration < 3: 
        sun_duration_ok = True
    if not sun_duration_ok: 
        return False
    if uv_index > 8 and sunlight_needs == ['part shade']: 
        return False
    if uv_index < 3 and sunlight_needs == ['full sun']: 
        return False

    # Rule 3: Watering requirements
    precipitation = agg_weather.get('avg_daily_precipitation', 0)
    watering_needs = plant.get('watering', '')
    if watering_needs == 'Frequent' and precipitation < 3: 
        return False
    if watering_needs == 'Minimal' and precipitation > 5: 
        return False
    if watering_needs == 'Average' and not (1 <= precipitation <= 8): 
        return False

    # Rule 4: Drought tolerance
    humidity = agg_weather.get('avg_relative_humidity', 0)
    if not plant.get('drought_tolerant', False) and humidity < 40: 
        return False

    return True

def get_plant_recommendations(latitude, longitude):
    """Main coordination function, executes the complete recommendation process."""
    print(f"\nGenerating plant recommendation report for coordinates ({latitude}, {longitude})...")
    
    plants = load_plants_from_db()
    if not plants:
        print("!! Unable to load plant data, recommendation process terminated.")
        return None, None
    
    agg_weather = get_and_aggregate_weather_data(latitude, longitude)
    if not agg_weather:
        print("!! Unable to retrieve weather data, recommendation process terminated.")
        return None, None
        
    # Filter suitable plants
    suitable_plants = []
    for plant in plants:
        if is_plant_suitable(agg_weather, plant):
            suitable_plants.append(plant)
    
    # Extract plant IDs and randomize order
    suitable_plant_ids = [plant['general_plant_id'] for plant in suitable_plants]
    random.shuffle(suitable_plant_ids)
    
    return agg_weather, suitable_plant_ids

# ==============================================================================
# 3. Main Execution Block
# ==============================================================================

if __name__ == "__main__":
    # Test function
    weather_info, plant_ids = get_plant_recommendations(latitude=-37.8136, longitude=144.9631)
    
    if weather_info and plant_ids is not None:
        print("\n" + "="*50)
        print("      Aggregated Weather Information for Next 16 Days      ")
        print("="*50)
        for key, value in weather_info.items():
            print(f"{key}: {value}")
        
        print("\n" + "="*50)
        print("      List of Plant IDs Meeting Growing Conditions (Randomized)      ")
        print("="*50)
        if plant_ids:
            print(plant_ids)
        else:
            print("Based on future weather, no plants were found that meet the specific conditions.")
        print("="*50)
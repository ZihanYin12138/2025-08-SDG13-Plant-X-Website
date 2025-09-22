# .py version of 01_plant_recommendation.ipynb
# Name: Zihan

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
import argparse  # <-- 新增：用于处理命令行参数

# ==============================================================================
# 1. 常量与配置 (Constants and Configuration)
# ==============================================================================

# 数据库连接配置
# 注意：在生产环境中，建议使用更安全的方式管理密码，例如环境变量。
DB_CONFIG = {
    'host': 'database-plantx.cqz06uycysiz.us-east-1.rds.amazonaws.com',
    'user': 'zihan',
    'password': '2002317Yzh12138.',
    'database': 'FIT5120_PlantX_Database',
    'use_pure': True,
    'charset': 'utf8mb4'
}

# 耐寒区到温度(°C)的转换表
HARDINESS_ZONE_TO_CELSIUS = {
    "1": -51.1, "2": -45.6, "3": -40.0, "4": -34.4, "5": -28.9,
    "6": -23.3, "7": -17.8, "8": -12.2, "9": -6.7, "10": -1.1,
    "11": 4.4,  "12": 10.0, "13": 15.6
}

# ==============================================================================
# 2. 函数定义 (Function Definitions)
# ==============================================================================

def load_plants_from_db(config):
    """从MySQL数据库加载植物数据并进行预处理。"""
    df_plants = pd.DataFrame() # 默认创建一个空的DataFrame
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("--> 成功连接到MySQL数据库...")
            query = "SELECT * FROM Table13_GeneralPlantListforRecommendation;"
            df_plants = pd.read_sql(query, connection)
            print(f"--> 成功从数据库加载 {len(df_plants)} 种植物。")
    except Error as e:
        print(f"!! 从MySQL加载数据时发生错误: {e}")
        return pd.DataFrame()
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("--> MySQL数据库连接已关闭。")

    if not df_plants.empty:
        df_plants['sunlight'] = df_plants['sunlight'].apply(json.loads)
        df_plants['drought_tolerant'] = df_plants['drought_tolerant'].astype(bool)
    
    return df_plants

def get_and_aggregate_weather_data(latitude, longitude):
    """根据经纬度获取并聚合天气数据。"""
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
        print(f"!! API请求失败: {e}")
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
    """核心匹配逻辑：判断单个植物是否符合天气条件。"""
    if agg_weather.get('extreme_min_temp') is None: return False # 如果天气数据无效，则无法判断
    
    # 规则 1: 生存底线
    if agg_weather['extreme_min_temp'] < plant_row['absolute_min_temp_c']:
        return False

    # 规则 2: 日照需求
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

    # 规则 3: 浇水需求
    precipitation = agg_weather.get('avg_daily_precipitation', 0)
    watering_needs = plant_row['watering']
    if watering_needs == 'Frequent' and precipitation < 3: return False
    if watering_needs == 'Minimal' and precipitation > 5: return False
    if watering_needs == 'Average' and not (1 <= precipitation <= 8): return False

    # 规则 4: 抗旱性
    humidity = agg_weather.get('avg_relative_humidity', 0)
    if not plant_row['drought_tolerant'] and humidity < 40: return False

    return True

def get_plant_recommendations(latitude, longitude):
    """主协调函数，执行完整的推荐流程。"""
    print(f"\n为经纬度 ({latitude}, {longitude}) 生成植物推荐报告...")
    
    df_plants = load_plants_from_db(DB_CONFIG)
    if df_plants.empty:
        print("!! 无法加载植物数据，推荐流程终止。")
        return None, None
    
    agg_weather = get_and_aggregate_weather_data(latitude, longitude)
    if not agg_weather:
        print("!! 无法获取天气数据，推荐流程终止。")
        return None, None
        
    is_suitable_series = df_plants.apply(lambda row: is_plant_suitable(agg_weather, row), axis=1)
    suitable_plant_ids = df_plants[is_suitable_series]['general_plant_id'].tolist()
    random.shuffle(suitable_plant_ids)
    
    return agg_weather, suitable_plant_ids

# ==============================================================================
# 3. 主执行模块 (Main Execution Block)
# ==============================================================================

if __name__ == "__main__":
    # --- 设置命令行参数解析 ---
    parser = argparse.ArgumentParser(description="根据未来16天天气预报推荐适宜植物。")
    parser.add_argument('--lat', type=float, default=-37.8136, help='目标地点的纬度 (例如: -37.8136)')
    parser.add_argument('--lon', type=float, default=144.9631, help='目标地点的经度 (例如: 144.9631)')
    # --- 【修改之处 1】新增 --json 参数 ---
    parser.add_argument('--json', action='store_true', help='以单一JSON格式输出结果，方便程序解析。')
    args = parser.parse_args()

    # --- 调用主函数并获取结果 ---
    weather_info, plant_ids = get_plant_recommendations(latitude=args.lat, longitude=args.lon)

    # --- 【修改之处 2】根据 --json 参数决定输出格式 ---
    if args.json:
        # 如果 --json 标志存在，则输出一个JSON对象
        if weather_info and plant_ids is not None:
            final_output = {
                "aggregated_weather": weather_info,
                "recommended_plant_ids": plant_ids
            }
            print(json.dumps(final_output, indent=4))
        else:
            # 即使失败也输出一个标准的JSON错误信息
            print(json.dumps({"error": "Failed to generate recommendations."}, indent=4))
    else:
        # 否则，输出便于人类阅读的格式化报告
        if weather_info and plant_ids is not None:
            print("\n" + "="*50)
            print("      未来16天聚合天气信息      ")
            print("="*50)
            for key, value in weather_info.items():
                print(f"{key}: {value}")
            
            print("\n" + "="*50)
            print("      符合种植条件的植物ID列表 (已随机排序)      ")
            print("="*50)
            if plant_ids:
                print(plant_ids)
            else:
                print("根据未来天气，未找到特别符合条件的植物。")
            print("="*50)
       
# python 01_plant_recommendation.py --lat -36.7570 --lon 144.2794
# python 01_plant_recommendation.py --lat -37.8749 --lon 145.0417 --json
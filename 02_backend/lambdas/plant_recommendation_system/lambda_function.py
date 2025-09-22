#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AWS Lambda Function Entry Point - Plant Recommendation System

This file serves as the entry point for the AWS Lambda function, handling requests from API Gateway
and calling the plant recommendation system to generate recommendation results.
"""

import json
import os
import sys
from typing import Dict, Any, Optional

# Add current directory to Python path to import plant_recommendation module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plant_recommendation_lambda import get_plant_recommendations

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda function handler
    
    Args:
        event: API Gateway event object
        context: Lambda context object
        
    Returns:
        Dictionary in API Gateway response format
    """
    try:
        # Validate required environment variables
        required_env_vars = ['DB_HOST', 'DB_NAME', 'DB_PASSWORD', 'DB_USER']
        missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
        if missing_vars:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Configuration Error',
                    'message': f'Missing required environment variables: {", ".join(missing_vars)}'
                })
            }
        
        # Parse request parameters
        if event.get('httpMethod') == 'GET':
            # Get latitude and longitude from query parameters
            query_params = event.get('queryStringParameters') or {}
            latitude = float(query_params.get('lat', -37.8136))
            longitude = float(query_params.get('lon', 144.9631))
        elif event.get('httpMethod') == 'POST':
            # Get latitude and longitude from request body
            try:
                body_str = event.get('body', '{}')
                if not body_str or body_str.strip() == '':
                    body_str = '{}'
                body = json.loads(body_str)
                latitude = float(body.get('latitude', -37.8136))
                longitude = float(body.get('longitude', 144.9631))
            except json.JSONDecodeError as e:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                    },
                    'body': json.dumps({
                    'error': 'JSON Parse Error',
                    'message': f'Request body is not valid JSON format: {str(e)}',
                        'expected_format': {
                            'latitude': -37.8136,
                            'longitude': 144.9631
                        }
                    })
                }
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Unsupported HTTP Method',
                    'message': 'Only GET and POST requests are supported'
                })
            }
        
        # Validate latitude and longitude range
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Invalid Coordinate Parameters',
                    'message': 'Latitude must be between -90 and 90, longitude must be between -180 and 180'
                })
            }
        
        # Call plant recommendation system
        weather_info, plant_ids = get_plant_recommendations(latitude, longitude)
        
        if weather_info is None or plant_ids is None:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Recommendation Generation Failed',
                    'message': 'Unable to retrieve weather data or plant data'
                })
            }
        
        # Build success response
        response_data = {
            'success': True,
            'latitude': latitude,
            'longitude': longitude,
            'aggregated_weather': weather_info,
            'recommended_plant_ids': plant_ids,
            'total_recommendations': len(plant_ids)
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps(response_data, ensure_ascii=False, indent=2)
        }
        
    except ValueError as e:
        # Parameter parsing error
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Parameter Error',
                'message': str(e)
            })
        }
        
    except Exception as e:
        # Other unexpected errors
        print(f"Lambda function execution error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': 'Recommendation system temporarily unavailable'
            })
        }

def handle_cors_preflight(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle CORS preflight request
    """
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': ''
    }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWS Lambda Function - Plant Disease Recognition Service
Get images from S3, use pre-trained model for disease recognition, return results
"""

import json
import os
import warnings
import base64
from io import BytesIO
from pathlib import Path

import boto3
import timm
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

# Ignore warning messages
warnings.filterwarnings('ignore')

# Global variables for caching model and configuration
model = None
class_map = None
inference_transforms = None

def load_class_map():
    """Load class mapping from local class_map.json file"""
    global class_map
    if class_map is None:
        try:
            with open('/opt/ml/class_map.json', 'r', encoding='utf-8') as f:
                class_map = json.load(f)
            # Convert string keys to integers
            class_map = {int(k): v for k, v in class_map.items()}
            print("✅ Class mapping loaded successfully")
        except Exception as e:
            print(f"🛑 Failed to load class mapping: {e}")
            class_map = {}
    return class_map

def load_model():
    """Load pre-trained plant disease recognition model"""
    global model, inference_transforms
    
    if model is not None:
        return model
    
    try:
        # Set device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {device}")
        
        # Define image preprocessing
        inference_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Load model
        num_classes = len(load_class_map())
        model = timm.create_model("swin_base_patch4_window7_224.ms_in1k", 
                                pretrained=False, 
                                num_classes=num_classes)
        
        # Load trained weights
        model_path = '/opt/ml/model.pth'
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval()
        
        print("✅ Model loaded successfully")
        return model
        
    except Exception as e:
        print(f"🛑 Model loading failed: {e}")
        return None

def get_latest_image_from_s3(bucket_name, prefix=""):
    """Get the latest image from S3 (sorted by upload time)"""
    try:
        s3_client = boto3.client('s3')
        
        # List all objects under specified prefix
        paginator = s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.jfif', '.avif'}
        all_image_objects = []
        
        # Iterate through all pages, collect all image objects
        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    # Check if it's an image file
                    if any(key.lower().endswith(ext) for ext in image_extensions):
                        all_image_objects.append(obj)
        
        if not all_image_objects:
            print(f"🛑 No image files found in {bucket_name}/{prefix}")
            return None, None
        
        # Sort by modification time, get the latest (last uploaded)
        latest_obj = max(all_image_objects, key=lambda x: x['LastModified'])
        latest_key = latest_obj['Key']
        latest_time = latest_obj['LastModified']
        
        print(f"🔍 Scanned {len(all_image_objects)} images")
        print(f"✅ Found latest image: {latest_key}")
        print(f"📅 Upload time: {latest_time}")
        print(f"📏 File size: {latest_obj['Size']} bytes")
        
        # Download image
        response = s3_client.get_object(Bucket=bucket_name, Key=latest_key)
        image_data = response['Body'].read()
        
        # Use PIL to open image
        image = Image.open(BytesIO(image_data)).convert("RGB")
        print(f"✅ Successfully downloaded image from S3: {latest_key}")
        print(f"🖼️ Image size: {image.size[0]}x{image.size[1]}")
        
        return image, latest_key
        
    except Exception as e:
        print(f"🛑 Failed to get latest image from S3: {e}")
        return None, None

def download_image_from_s3(bucket_name, object_key):
    """Download specified image from S3"""
    try:
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        image_data = response['Body'].read()
        
        # Use PIL to open image
        image = Image.open(BytesIO(image_data)).convert("RGB")
        print(f"✅ Successfully downloaded image from S3: {object_key}")
        return image
        
    except Exception as e:
        print(f"🛑 Failed to download image from S3: {e}")
        return None

def predict_image(image, topk=3):
    """Perform disease prediction on image"""
    global model, inference_transforms, class_map
    
    if model is None or inference_transforms is None:
        return None
    
    try:
        # Preprocess image
        image_tensor = inference_transforms(image).unsqueeze(0)
        device = next(model.parameters()).device
        image_tensor = image_tensor.to(device)
        
        # Model inference
        with torch.no_grad():
            logits = model(image_tensor)
        
        # Calculate probabilities
        probabilities = F.softmax(logits, dim=1)
        topk_probs, topk_indices = torch.topk(probabilities, topk, dim=1)
        
        topk_probs = topk_probs.squeeze().cpu().numpy()
        topk_indices = topk_indices.squeeze().cpu().numpy()
        
        # Build results
        results = []
        for i in range(topk):
            class_idx = topk_indices[i]
            class_id = class_map.get(class_idx, class_idx)
            prob = topk_probs[i]
            
            results.append({
                "predicted_id": int(class_id),
                "probability": float(prob),
                "confidence": f"{prob:.2%}"
            })
        
        return results
        
    except Exception as e:
        print(f"🛑 Image prediction failed: {e}")
        return None

def lambda_handler(event, context):
    """
    AWS Lambda main handler function - called via API Gateway
    
    Workflow:
    1. Receive API Gateway request
    2. Get latest image from S3
    3. Use model for disease recognition
    4. Return recognition results
    
    Environment variables:
    - S3_BUCKET: S3 bucket name
    - S3_PREFIX: S3 object prefix (optional, for filtering images)
    - TOPK: Return top K results, default is 3
    
    API request format:
    GET/POST https://your-api-gateway-url/predict
    Optional parameters:
    - topk: Return top K results (default 3)
    - prefix: S3 prefix (overrides environment variable)
    """
    
    try:
        # Get environment variables
        s3_bucket = os.environ.get('S3_BUCKET')
        s3_prefix = os.environ.get('S3_PREFIX', '')
        topk = int(os.environ.get('TOPK', 3))
        
        # Process API Gateway request
        print(f"🚀 API Gateway invocation started")
        print(f"📋 Request event: {json.dumps(event, indent=2)}")
        
        # Get parameters from API Gateway request
        if 'queryStringParameters' in event and event['queryStringParameters']:
            # GET request parameters
            params = event['queryStringParameters']
            if 'topk' in params:
                topk = int(params['topk'])
            if 'prefix' in params:
                s3_prefix = params['prefix']
        elif 'body' in event and event['body']:
            # POST request parameters
            try:
                body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
                if 'topk' in body:
                    topk = int(body['topk'])
                if 'prefix' in body:
                    s3_prefix = body['prefix']
            except json.JSONDecodeError:
                print("⚠️ Could not parse request body, using default parameters")
        
        # Validate required parameters
        if not s3_bucket:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Configuration error',
                    'message': 'Missing environment variable S3_BUCKET'
                }, ensure_ascii=False)
            }
        
        # Load model (if not already loaded)
        if model is None:
            load_model()
            load_class_map()
        
        if model is None:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Model loading failed',
                    'message': 'Could not load plant disease recognition model'
                }, ensure_ascii=False)
            }
        
        # Get latest image (main function of API Gateway invocation)
        print(f"🔍 Getting latest image from S3: s3://{s3_bucket}/{s3_prefix}")
        print(f"💡 This will process the latest image just uploaded by the upload Lambda")
        
        image, image_key = get_latest_image_from_s3(s3_bucket, s3_prefix)
        
        if image is None:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Image retrieval failed',
                    'message': f'Could not retrieve image from S3: s3://{s3_bucket}/{s3_prefix}'
                }, ensure_ascii=False)
            }
        
        # Perform prediction
        predictions = predict_image(image, topk)
        if predictions is None:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Prediction failed',
                    'message': 'An error occurred during image prediction'
                }, ensure_ascii=False)
            }
        
        # Return successful result
        response_body = {
            'status': 'success',
            'message': 'Plant disease recognition completed',
            'image_info': {
                'bucket': s3_bucket,
                'key': image_key,
                'size': f"{image.size[0]}x{image.size[1]}",
                'is_latest': True  # Identify if it's the latest image
            },
            'predictions': predictions,
            'top_prediction': predictions[0] if predictions else None
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body, ensure_ascii=False, indent=2)
        }
        
    except Exception as e:
        print(f"🛑 Lambda function execution error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            }, ensure_ascii=False)
        }

# Helper function for testing
def test_local():
    """Local test function - simulates API Gateway invocation"""
    # Simulate environment variables
    os.environ['S3_BUCKET'] = 'plant-disease-images'
    os.environ['S3_PREFIX'] = 'uploads/'
    os.environ['TOPK'] = '3'
    
    # Test 1: GET request (with query parameters)
    print("=== Test 1: GET Request - With Query Parameters ===")
    print("💡 Scenario: GET /predict?topk=5&prefix=uploads/")
    test_event_get = {
        "httpMethod": "GET",
        "queryStringParameters": {
            "topk": "5",
            "prefix": "uploads/"
        },
        "headers": {
            "Content-Type": "application/json"
        }
    }
    result = lambda_handler(test_event_get, None)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Test 2: POST request (with request body)
    print("\n=== Test 2: POST Request - With Request Body ===")
    print("💡 Scenario: POST /predict with JSON body")
    test_event_post = {
        "httpMethod": "POST",
        "body": json.dumps({
            "topk": 3,
            "prefix": "uploads/"
        }),
        "headers": {
            "Content-Type": "application/json"
        }
    }
    result = lambda_handler(test_event_post, None)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Test 3: Simple GET request (using default parameters)
    print("\n=== Test 3: Simple GET Request - Using Default Parameters ===")
    print("💡 Scenario: GET /predict (using environment variable defaults)")
    test_event_simple = {
        "httpMethod": "GET",
        "queryStringParameters": None,
        "headers": {
            "Content-Type": "application/json"
        }
    }
    result = lambda_handler(test_event_simple, None)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Test 4: Error case - missing configuration
    print("\n=== Test 4: Error Case - Missing S3_BUCKET Configuration ===")
    os.environ.pop('S3_BUCKET', None)  # Temporarily remove environment variable
    test_event_error = {
        "httpMethod": "GET",
        "queryStringParameters": None,
        "headers": {
            "Content-Type": "application/json"
        }
    }
    result = lambda_handler(test_event_error, None)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    os.environ['S3_BUCKET'] = 'plant-disease-images'  # Restore environment variable

if __name__ == "__main__":
    test_local()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWS Lambda函数 - 植物病害识别服务
从S3获取图片，使用预训练模型进行病害识别，返回结果
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

# 忽略警告信息
warnings.filterwarnings('ignore')

# 全局变量，用于缓存模型和配置
model = None
class_map = None
inference_transforms = None

def load_class_map():
    """从本地class_map.json文件加载类别映射"""
    global class_map
    if class_map is None:
        try:
            with open('/opt/ml/class_map.json', 'r', encoding='utf-8') as f:
                class_map = json.load(f)
            # 将字符串键转换为整数
            class_map = {int(k): v for k, v in class_map.items()}
            print("✅ 类别映射加载成功")
        except Exception as e:
            print(f"🛑 加载类别映射失败: {e}")
            class_map = {}
    return class_map

def load_model():
    """加载预训练的植物病害识别模型"""
    global model, inference_transforms
    
    if model is not None:
        return model
    
    try:
        # 设置设备
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用设备: {device}")
        
        # 定义图像预处理
        inference_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # 加载模型
        num_classes = len(load_class_map())
        model = timm.create_model("swin_base_patch4_window7_224.ms_in1k", 
                                pretrained=False, 
                                num_classes=num_classes)
        
        # 加载训练好的权重
        model_path = '/opt/ml/model.pth'
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval()
        
        print("✅ 模型加载成功")
        return model
        
    except Exception as e:
        print(f"🛑 模型加载失败: {e}")
        return None

def get_latest_image_from_s3(bucket_name, prefix=""):
    """从S3获取最新的图片（按上传时间排序）"""
    try:
        s3_client = boto3.client('s3')
        
        # 列出指定前缀下的所有对象
        paginator = s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.jfif', '.avif'}
        all_image_objects = []
        
        # 遍历所有页面，收集所有图片对象
        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    # 检查是否为图片文件
                    if any(key.lower().endswith(ext) for ext in image_extensions):
                        all_image_objects.append(obj)
        
        if not all_image_objects:
            print(f"🛑 在 {bucket_name}/{prefix} 中没有找到图片文件")
            return None, None
        
        # 按修改时间排序，获取最新的（最后上传的）
        latest_obj = max(all_image_objects, key=lambda x: x['LastModified'])
        latest_key = latest_obj['Key']
        latest_time = latest_obj['LastModified']
        
        print(f"🔍 扫描了 {len(all_image_objects)} 张图片")
        print(f"✅ 找到最新图片: {latest_key}")
        print(f"📅 上传时间: {latest_time}")
        print(f"📏 文件大小: {latest_obj['Size']} bytes")
        
        # 下载图片
        response = s3_client.get_object(Bucket=bucket_name, Key=latest_key)
        image_data = response['Body'].read()
        
        # 使用PIL打开图片
        image = Image.open(BytesIO(image_data)).convert("RGB")
        print(f"✅ 成功从S3下载图片: {latest_key}")
        print(f"🖼️ 图片尺寸: {image.size[0]}x{image.size[1]}")
        
        return image, latest_key
        
    except Exception as e:
        print(f"🛑 从S3获取最新图片失败: {e}")
        return None, None

def download_image_from_s3(bucket_name, object_key):
    """从S3下载指定图片"""
    try:
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        image_data = response['Body'].read()
        
        # 使用PIL打开图片
        image = Image.open(BytesIO(image_data)).convert("RGB")
        print(f"✅ 成功从S3下载图片: {object_key}")
        return image
        
    except Exception as e:
        print(f"🛑 从S3下载图片失败: {e}")
        return None

def predict_image(image, topk=3):
    """对图片进行病害预测"""
    global model, inference_transforms, class_map
    
    if model is None or inference_transforms is None:
        return None
    
    try:
        # 预处理图片
        image_tensor = inference_transforms(image).unsqueeze(0)
        device = next(model.parameters()).device
        image_tensor = image_tensor.to(device)
        
        # 模型推理
        with torch.no_grad():
            logits = model(image_tensor)
        
        # 计算概率
        probabilities = F.softmax(logits, dim=1)
        topk_probs, topk_indices = torch.topk(probabilities, topk, dim=1)
        
        topk_probs = topk_probs.squeeze().cpu().numpy()
        topk_indices = topk_indices.squeeze().cpu().numpy()
        
        # 构建结果
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
        print(f"🛑 图片预测失败: {e}")
        return None

def lambda_handler(event, context):
    """
    AWS Lambda主处理函数 - 通过API Gateway调用
    
    工作流程:
    1. 接收API Gateway请求
    2. 从S3获取最新图片
    3. 使用模型进行病害识别
    4. 返回识别结果
    
    环境变量:
    - S3_BUCKET: S3存储桶名称
    - S3_PREFIX: S3对象前缀（可选，用于筛选图片）
    - TOPK: 返回前K个结果，默认为3
    
    API请求格式:
    GET/POST https://your-api-gateway-url/predict
    可选参数:
    - topk: 返回前K个结果（默认3）
    - prefix: S3前缀（覆盖环境变量）
    """
    
    try:
        # 获取环境变量
        s3_bucket = os.environ.get('S3_BUCKET')
        s3_prefix = os.environ.get('S3_PREFIX', '')
        topk = int(os.environ.get('TOPK', 3))
        
        # 处理API Gateway请求
        print(f"🚀 API Gateway调用开始")
        print(f"📋 请求事件: {json.dumps(event, indent=2)}")
        
        # 从API Gateway请求中获取参数
        if 'queryStringParameters' in event and event['queryStringParameters']:
            # GET请求参数
            params = event['queryStringParameters']
            if 'topk' in params:
                topk = int(params['topk'])
            if 'prefix' in params:
                s3_prefix = params['prefix']
        elif 'body' in event and event['body']:
            # POST请求参数
            try:
                body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
                if 'topk' in body:
                    topk = int(body['topk'])
                if 'prefix' in body:
                    s3_prefix = body['prefix']
            except json.JSONDecodeError:
                print("⚠️ 无法解析请求体，使用默认参数")
        
        # 验证必需参数
        if not s3_bucket:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': '配置错误',
                    'message': '缺少环境变量 S3_BUCKET'
                }, ensure_ascii=False)
            }
        
        # 加载模型（如果尚未加载）
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
                    'error': '模型加载失败',
                    'message': '无法加载植物病害识别模型'
                }, ensure_ascii=False)
            }
        
        # 获取最新图片（API Gateway调用的主要功能）
        print(f"🔍 从S3获取最新图片: s3://{s3_bucket}/{s3_prefix}")
        print(f"💡 这将处理上传Lambda刚上传的最新图片")
        
        image, image_key = get_latest_image_from_s3(s3_bucket, s3_prefix)
        
        if image is None:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': '图片获取失败',
                    'message': f'无法从S3获取图片: s3://{s3_bucket}/{s3_prefix}'
                }, ensure_ascii=False)
            }
        
        # 进行预测
        predictions = predict_image(image, topk)
        if predictions is None:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': '预测失败',
                    'message': '图片预测过程中出现错误'
                }, ensure_ascii=False)
            }
        
        # 返回成功结果
        response_body = {
            'status': 'success',
            'message': '植物病害识别完成',
            'image_info': {
                'bucket': s3_bucket,
                'key': image_key,
                'size': f"{image.size[0]}x{image.size[1]}",
                'is_latest': True  # 标识是否为最新图片
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
        print(f"🛑 Lambda函数执行错误: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': '服务器内部错误',
                'message': str(e)
            }, ensure_ascii=False)
        }

# 用于测试的辅助函数
def test_local():
    """本地测试函数 - 模拟API Gateway调用"""
    # 模拟环境变量
    os.environ['S3_BUCKET'] = 'plant-disease-images'
    os.environ['S3_PREFIX'] = 'uploads/'
    os.environ['TOPK'] = '3'
    
    # 测试1: GET请求（带查询参数）
    print("=== 测试1: GET请求 - 带查询参数 ===")
    print("💡 场景：GET /predict?topk=5&prefix=uploads/")
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
    
    # 测试2: POST请求（带请求体）
    print("\n=== 测试2: POST请求 - 带请求体 ===")
    print("💡 场景：POST /predict with JSON body")
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
    
    # 测试3: 简单GET请求（使用默认参数）
    print("\n=== 测试3: 简单GET请求 - 使用默认参数 ===")
    print("💡 场景：GET /predict（使用环境变量默认值）")
    test_event_simple = {
        "httpMethod": "GET",
        "queryStringParameters": None,
        "headers": {
            "Content-Type": "application/json"
        }
    }
    result = lambda_handler(test_event_simple, None)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 测试4: 错误情况 - 缺少配置
    print("\n=== 测试4: 错误情况 - 缺少S3_BUCKET配置 ===")
    os.environ.pop('S3_BUCKET', None)  # 临时移除环境变量
    test_event_error = {
        "httpMethod": "GET",
        "queryStringParameters": None,
        "headers": {
            "Content-Type": "application/json"
        }
    }
    result = lambda_handler(test_event_error, None)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    os.environ['S3_BUCKET'] = 'plant-disease-images'  # 恢复环境变量

if __name__ == "__main__":
    test_local()

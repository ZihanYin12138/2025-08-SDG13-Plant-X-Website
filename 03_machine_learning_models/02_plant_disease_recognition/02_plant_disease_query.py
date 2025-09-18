#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Description: Plant disease classification inference script.

# 1. 标准库 (Standard Library)
import argparse
import json
import warnings
from pathlib import Path

# 2. 第三方库 (Third-party Libraries)
import timm
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

# ====================================================================
# 1. 全局设置与辅助函数
# ====================================================================

# 忽略一些不影响结果的警告信息
warnings.filterwarnings('ignore')

# 推理时使用的图像转换，必须与训练时的验证/测试集转换完全一致
inference_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_class_map(json_path: Path):
    """从JSON文件加载 索引 -> ID 的映射字典"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            idx_to_label = json.load(f)
        # JSON加载的key默认是字符串，我们需要将其转为整数以匹配PyTorch的输出
        idx_to_label = {int(k): v for k, v in idx_to_label.items()}
        print("✅ 翻译词典加载成功。")
        return idx_to_label
    except Exception as e:
        print(f"🛑 加载映射文件 '{json_path}' 时出错: {e}")
        return None

def load_model(model_name: str, num_classes: int, model_path: Path, device: torch.device):
    """加载模型架构并载入训练好的权重"""
    try:
        model = timm.create_model(model_name, pretrained=False, num_classes=num_classes)
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval() # 切换到评估模式，这非常重要！
        print("✅ 模型加载成功。")
        return model
    except Exception as e:
        print(f"🛑 加载模型 '{model_path}' 时出错: {e}")
        return None

def predict_topk(model: nn.Module, image_path: Path, transforms: transforms.Compose, 
                 idx_to_label_map: dict, device: torch.device, k: int = 3):
    """对单张图片进行Top-K预测，只输出ID和概率"""
    try:
        image = Image.open(image_path).convert("RGB")
        image_tensor = transforms(image).unsqueeze(0).to(device)
    except Exception as e:
        print(f"🛑 处理图片 '{image_path}' 时出错: {e}")
        return None

    with torch.no_grad():
        logits = model(image_tensor)

    probabilities = F.softmax(logits, dim=1)
    topk_probs, topk_indices = torch.topk(probabilities, k, dim=1)

    topk_probs = topk_probs.squeeze().cpu().numpy()
    topk_indices = topk_indices.squeeze().cpu().numpy()
    
    results = []
    for i in range(k):
        class_idx = topk_indices[i]
        class_id = idx_to_label_map[class_idx]
        prob = topk_probs[i]
        
        results.append({
            "predicted_id": int(class_id),
            "probability": float(prob) # 返回浮点数而不是字符串，方便后续处理
        })
        
    return results

# ====================================================================
# 2. 主程序
# ====================================================================

def main():
    # --- 设置命令行参数 ---
    ap = argparse.ArgumentParser(description="植物病害识别推理脚本")
    ap.add_argument("--image", type=str, required=True, help="需要预测的单张图片路径")
    ap.add_argument("--model-path", type=str, default="model.pth", help="训练好的模型文件路径 (.pth)")
    ap.add_argument("--class-map", type=str, default="class_map.json", help="类别索引到ID的映射文件 (.json)")
    ap.add_argument("--topk", type=int, default=3, help="返回概率最高的K个结果")
    ap.add_argument("--json", action="store_true", help="如果设置，则以JSON格式输出结果")
    args = ap.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")

    # --- 将路径字符串转换为Path对象 ---
    model_path = Path(args.model_path)
    class_map_path = Path(args.class_map)
    image_path = Path(args.image)

    # --- 执行流程 ---
    idx_to_label = load_class_map(class_map_path)
    if not idx_to_label:
        return

    model = load_model("swin_base_patch4_window7_224.ms_in1k", len(idx_to_label), model_path, device)
    if not model:
        return
        
    if not image_path.exists():
        print(f"🛑 错误: 输入图片 '{image_path}' 不存在。")
        return

    results = predict_topk(model, image_path, inference_transforms, idx_to_label, device, k=args.topk)

    # --- 输出结果 ---
    if not results:
        print("🛑 预测失败。")
        return

    if args.json:
        # 以JSON格式输出
        # ensure_ascii=False 确保中文等非ASCII字符能正确显示
        print(json.dumps(results, indent=4, ensure_ascii=False))
    else:
        # 以人类可读的格式输出
        print("\n" + "="*30)
        print("--- 预测结果 ---")
        print(f"图片: {image_path.name}")
        print("="*30)
        for pred in results:
            print(f"病害ID: {pred['predicted_id']:<5} | 概率: {pred['probability']:.2%}")

# ====================================================================
# 3. 程序主入口
# ====================================================================

if __name__ == "__main__":
    main()

# ====================================================================
# 4. 使用示例 (在终端中运行)
# ====================================================================
#
# python 02_plant_disease_query.py --image test_images/011d0.jfif
#
# python 02_plant_disease_query.py --image test_images/011d0.jfif --topk 3 --json
#
# python 02_plant_disease_query.py --image test_images/Appels.jfif --topk 3 --json
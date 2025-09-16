# .py version of 02_plant_image_query.ipynb
# Name: Zihan Yin

#!/usr/bin/env python3
import argparse, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

import torch
from torch import nn
from torchvision import transforms
from transformers import CLIPModel, CLIPProcessor


# ============ A lot of Helper Functions here ============

def exif_correct(img: Image.Image) -> Image.Image:
    """纠正方向 & 转换为 RGB"""
    img = ImageOps.exif_transpose(img)
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255,255,255))
        bg.paste(img, mask=img.split()[-1])
        return bg
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def tta_pipeline():
    """轻量测试时增强"""
    return transforms.Compose([
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomAffine(degrees=10, translate=(0.06, 0.06), scale=(0.95, 1.05)),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.01),
    ])


@torch.no_grad()
def encode_query(img: Image.Image, model, processor, device, tta_num=8):
    """对用户上传的图片做 TTA 编码，返回单一向量"""
    img = exif_correct(img)
    tta = tta_pipeline()
    pil_list = [img] + [tta(img) for _ in range(max(tta_num-1, 0))]

    inputs = processor(images=pil_list, return_tensors="pt", do_center_crop=True, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.autocast(device_type=("cuda" if device=="cuda" else "cpu"),
                        dtype=torch.float16, enabled=(device=="cuda")):
        feats = model.get_image_features(**inputs)
    feats = nn.functional.normalize(feats, p=2, dim=-1)
    q = feats.mean(dim=0, keepdim=False)  # (D,)
    return q.cpu().numpy().astype(np.float32)


def topk_cosine(query_emb, db_emb, plant_ids, k=10):
    """计算 Top-K cosine similarity"""
    sims = db_emb @ query_emb  # 余弦相似度
    idx = np.argpartition(-sims, kth=min(k, len(sims)-1))[:k]
    idx = idx[np.argsort(-sims[idx])]
    return [(int(plant_ids[i]), float(sims[i])) for i in idx]


# ============ Main Program ============

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", type=str, required=True, help="查询图片路径 (.jpg/.jpeg/.png)")
    ap.add_argument("--index", type=str, default="index/embeddings_fp16.npz", help="建库生成的索引文件")
    ap.add_argument("--meta", type=str, default="index/meta.json", help="建库生成的 meta 文件")
    ap.add_argument("--model-local", type=str, default="clip-vit-b32", help="本地保存的 CLIP 模型目录")
    ap.add_argument("--fallback-model-id", type=str, default="openai/clip-vit-base-patch32", help="若本地未找到则在线下载")
    ap.add_argument("--tta", type=int, default=8, help="TTA 次数（含原图）")
    ap.add_argument("--k", type=int, default=10, help="返回 Top-K 数量")
    ap.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    args = ap.parse_args()

    # 加载索引
    npz = np.load(args.index)
    db_emb = npz["embeddings"].astype(np.float32)  # (N, D)
    plant_ids = npz["plant_ids"]

    # 加载模型（优先使用在线模型）
    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:    
        print("尝试在线下载模型")
        model = CLIPModel.from_pretrained(args.fallback_model_id)
        processor = CLIPProcessor.from_pretrained(args.fallback_model_id)
    except Exception:
        print("尝试在线下载模型失败，尝试加载本地模型")
        model = CLIPModel.from_pretrained(args.model_local)
        processor = CLIPProcessor.from_pretrained(args.model_local)

    model.eval().to(device)

    # 读取查询图并编码
    img = Image.open(args.image)
    q_emb = encode_query(img, model, processor, device, tta_num=args.tta)

    # 相似度检索
    results = topk_cosine(q_emb, db_emb, plant_ids, k=args.k)

    # 输出
    if args.json:
        print(json.dumps([{"plant_id": pid, "score": score} for pid, score in results],
                         ensure_ascii=False, indent=2))
    else:
        for pid, score in results:
            print(f"{pid}\t{score:.4f}")


if __name__ == "__main__":
    main()

# 测试
# python 03_plant_image_query.py --image test_images/微信图片_20250903174840_68_7.jpg --k 10 --tta 8 --json
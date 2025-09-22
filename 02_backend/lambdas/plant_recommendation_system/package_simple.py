#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化的Lambda打包脚本
确保包含所有必需文件
"""

import os
import zipfile
from pathlib import Path

def create_lambda_package():
    """创建Lambda部署包"""
    
    # 当前目录
    current_dir = Path(".")
    
    # 创建ZIP文件
    zip_filename = "plant_recommendation_lambda.zip"
    
    print(f"创建Lambda部署包: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加主要文件
        main_files = [
            "lambda_function.py",
            "plant_recommendation_lambda.py"
        ]
        
        for file in main_files:
            if os.path.exists(file):
                print(f"添加文件: {file}")
                zipf.write(file, file)
        
        # 添加目录
        directories = [
            "common",
            "pymysql", 
            "requests",
            "urllib3",
            "certifi",
            "charset_normalizer",
            "idna"
        ]
        
        for dir_name in directories:
            if os.path.exists(dir_name):
                print(f"添加目录: {dir_name}")
                for root, dirs, files in os.walk(dir_name):
                    # 排除__pycache__目录
                    dirs[:] = [d for d in dirs if d != '__pycache__']
                    
                    for file in files:
                        # 排除.pyc文件
                        if not file.endswith('.pyc'):
                            file_path = os.path.join(root, file)
                            arcname = file_path
                            print(f"  添加: {arcname}")
                            zipf.write(file_path, arcname)
    
    print(f"\n✅ Lambda部署包创建完成: {zip_filename}")
    
    # 显示ZIP文件信息
    zip_size = os.path.getsize(zip_filename)
    print(f"文件大小: {zip_size / 1024 / 1024:.2f} MB")
    
    # 验证idna文件
    print("\n验证idna文件:")
    with zipfile.ZipFile(zip_filename, 'r') as z:
        idna_files = [f for f in z.namelist() if f.startswith('idna/')]
        for f in sorted(idna_files):
            print(f"  {f}")
    
    return zip_filename

if __name__ == "__main__":
    print("开始创建Lambda部署包...")
    zip_file = create_lambda_package()
    print(f"\n🎉 部署包已创建: {zip_file}")

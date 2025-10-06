#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simplified Lambda packaging script
Ensure all required files are included
"""

import os
import zipfile
from pathlib import Path

def create_lambda_package():
    """Create Lambda deployment package"""
    
    # Current directory
    current_dir = Path(".")
    
    # Create ZIP file
    zip_filename = "plant_recommendation_lambda.zip"
    
    print(f"Creating Lambda deployment package: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main files
        main_files = [
            "lambda_function.py",
            "plant_recommendation_lambda.py"
        ]
        
        for file in main_files:
            if os.path.exists(file):
                print(f"Adding file: {file}")
                zipf.write(file, file)
        
        # Add directories
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
                print(f"Adding directory: {dir_name}")
                for root, dirs, files in os.walk(dir_name):
                    # Exclude __pycache__ directories
                    dirs[:] = [d for d in dirs if d != '__pycache__']
                    
                    for file in files:
                        # Exclude .pyc files
                        if not file.endswith('.pyc'):
                            file_path = os.path.join(root, file)
                            arcname = file_path
                            print(f"  Adding: {arcname}")
                            zipf.write(file_path, arcname)
    
    print(f"\n✅ Lambda deployment package created: {zip_filename}")
    
    # Display ZIP file information
    zip_size = os.path.getsize(zip_filename)
    print(f"File size: {zip_size / 1024 / 1024:.2f} MB")
    
    # Verify idna files
    print("\nVerifying idna files:")
    with zipfile.ZipFile(zip_filename, 'r') as z:
        idna_files = [f for f in z.namelist() if f.startswith('idna/')]
        for f in sorted(idna_files):
            print(f"  {f}")
    
    return zip_filename

if __name__ == "__main__":
    print("Starting Lambda deployment package creation...")
    zip_file = create_lambda_package()
    print(f"\n🎉 Deployment package created: {zip_file}")

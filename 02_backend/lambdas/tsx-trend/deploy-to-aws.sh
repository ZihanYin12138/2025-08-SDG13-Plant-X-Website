#!/bin/bash

# 完整的AWS部署脚本
# 使用方法: ./deploy-to-aws.sh

set -e  # 遇到错误时退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
AWS_REGION="us-east-1"
ECR_REPOSITORY="plantx-tsx-trend-api"
IMAGE_TAG="latest"
APP_NAME="plantx-tsx-trend-api"

echo -e "${BLUE}🚀 开始部署 PlantX TSX Trend API 到 AWS...${NC}"

# 检查AWS CLI是否安装
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI 未安装。请先安装 AWS CLI。${NC}"
    exit 1
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装。请先安装 Docker。${NC}"
    exit 1
fi

# 获取AWS账户ID
echo -e "${YELLOW}📋 获取AWS账户信息...${NC}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✅ AWS账户ID: $AWS_ACCOUNT_ID${NC}"

# 1. 构建Docker镜像
echo -e "${YELLOW}📦 构建Docker镜像...${NC}"
docker build -t $ECR_REPOSITORY:$IMAGE_TAG .
echo -e "${GREEN}✅ Docker镜像构建完成${NC}"

# 2. 登录到ECR
echo -e "${YELLOW}🔐 登录到Amazon ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
echo -e "${GREEN}✅ ECR登录成功${NC}"

# 3. 创建ECR仓库（如果不存在）
echo -e "${YELLOW}📁 检查/创建ECR仓库...${NC}"
if aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null; then
    echo -e "${GREEN}✅ ECR仓库已存在${NC}"
else
    echo -e "${YELLOW}📁 创建ECR仓库...${NC}"
    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION
    echo -e "${GREEN}✅ ECR仓库创建成功${NC}"
fi

# 4. 标记镜像
echo -e "${YELLOW}🏷️ 标记镜像...${NC}"
docker tag $ECR_REPOSITORY:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG
echo -e "${GREEN}✅ 镜像标记完成${NC}"

# 5. 推送镜像到ECR
echo -e "${YELLOW}⬆️ 推送镜像到ECR...${NC}"
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG
echo -e "${GREEN}✅ 镜像推送成功${NC}"

# 6. 检查Terraform是否可用
if command -v terraform &> /dev/null; then
    echo -e "${YELLOW}🏗️ 使用Terraform部署基础设施...${NC}"
    cd terraform
    
    # 初始化Terraform
    terraform init
    
    # 计划部署
    terraform plan -var="aws_region=$AWS_REGION" -var="app_name=$APP_NAME"
    
    # 应用部署
    echo -e "${YELLOW}⚠️ 即将部署基础设施，请确认继续...${NC}"
    read -p "继续部署? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply -var="aws_region=$AWS_REGION" -var="app_name=$APP_NAME" -auto-approve
        echo -e "${GREEN}✅ Terraform部署完成${NC}"
    else
        echo -e "${YELLOW}⏭️ 跳过Terraform部署${NC}"
    fi
    
    cd ..
else
    echo -e "${YELLOW}⚠️ Terraform未安装，跳过基础设施部署${NC}"
    echo -e "${BLUE}💡 提示：您可以手动使用AWS控制台或CLI创建ECS服务${NC}"
fi

echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${BLUE}📋 部署信息：${NC}"
echo -e "   • 镜像URI: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG"
echo -e "   • 区域: $AWS_REGION"
echo -e "   • 应用名称: $APP_NAME"

echo -e "${BLUE}🔗 下一步：${NC}"
echo -e "   1. 在AWS控制台中创建ECS服务"
echo -e "   2. 使用提供的镜像URI"
echo -e "   3. 配置负载均衡器（如需要）"
echo -e "   4. 设置域名和SSL证书（如需要）"

echo -e "${GREEN}✅ 部署脚本执行完成！${NC}"



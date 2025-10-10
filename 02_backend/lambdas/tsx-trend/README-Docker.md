# TSX Trend API Docker 部署指南

## 📋 概述

这个项目使用Docker容器化Flask应用，可以部署到AWS ECS或EC2上。

## 🚀 本地开发

### 1. 使用Docker Compose（推荐）

```bash
# 构建并启动服务
docker-compose up --build

# 后台运行
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 2. 直接使用Docker

```bash
# 构建镜像
docker build -t tsx-trend-api .

# 运行容器
docker run -p 5000:5000 tsx-trend-api

# 后台运行
docker run -d -p 5000:5000 --name tsx-trend-api tsx-trend-api
```

## ☁️ AWS部署

### 方法1: 使用部署脚本（推荐）

1. 确保已安装AWS CLI并配置好凭证
2. 运行部署脚本：

```bash
chmod +x aws-deploy.sh
./aws-deploy.sh
```

### 方法2: 手动部署

#### 1. 构建并推送到ECR

```bash
# 设置变量
AWS_REGION="us-east-1"
ECR_REPOSITORY="plantx-tsx-trend-api"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 构建镜像
docker build -t $ECR_REPOSITORY .

# 登录ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 标记镜像
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

# 创建ECR仓库
aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

# 推送镜像
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
```

#### 2. 部署到ECS

1. 更新 `ecs-task-definition.json` 中的账户ID
2. 注册任务定义：

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

3. 创建ECS服务或使用现有服务

## 🔧 配置说明

### 环境变量

- `FLASK_ENV`: 设置为 `production` 用于生产环境
- 数据库连接信息在代码中硬编码，生产环境建议使用环境变量

### 端口

- 应用运行在端口 5000
- 容器内部端口：5000
- 外部访问端口：5000

## 📊 健康检查

应用包含以下健康检查端点：

- `GET /api/map/geojson` - 基础健康检查
- `GET /api/map/data/{year}` - 年份数据
- `GET /api/chart/data/{state}` - 州时间序列数据

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库配置
   - 确保网络连接正常
   - 验证数据库凭据

2. **端口冲突**
   - 更改docker-compose.yml中的端口映射
   - 或使用 `docker run -p 其他端口:5000`

3. **内存不足**
   - 增加ECS任务定义中的内存分配
   - 或调整Docker容器的内存限制

### 查看日志

```bash
# Docker Compose
docker-compose logs -f

# 直接Docker
docker logs -f tsx-trend-api

# ECS
aws logs tail /ecs/plantx-tsx-trend-api --follow
```

## 📝 API端点

- `GET /api/map/geojson` - 获取地图GeoJSON数据
- `GET /api/map/data/{year}` - 获取指定年份的choropleth数据
- `GET /api/chart/data/{state}` - 获取指定州的时间序列数据

## 🔒 安全注意事项

1. 生产环境中不要硬编码数据库密码
2. 使用AWS Secrets Manager或环境变量存储敏感信息
3. 配置适当的IAM角色和权限
4. 启用VPC和网络安全组



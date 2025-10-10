# PlantX TSX Trend API

## 🚀 快速部署指南

### 当前状态
- ✅ 已成功部署到AWS ECS
- ✅ 所有API端点正常工作
- ✅ 访问地址: `http://54.166.219.154:5000`

### 📁 核心文件说明

#### 应用文件
- `04_epic7_backend_sql.py` - 主要的Flask应用
- `requirements.txt` - Python依赖

#### Docker部署
- `Dockerfile` - Docker镜像构建文件
- `docker-compose.yml` - 本地开发环境

#### ECS部署
- `ecs-task-definition-fixed-health.json` - ECS任务定义
- `ecs-task-role-policy.json` - IAM任务角色策略
- `ecs-execution-role-policy.json` - IAM执行角色策略
- `deploy-to-aws.sh` - AWS部署脚本

#### Terraform基础设施
- `terraform/` - 基础设施即代码配置

### 🔧 重新部署步骤

#### 1. 本地测试
```bash
# 构建并运行Docker容器
docker-compose up -d

# 测试API
curl http://localhost:5000/api/map/data/2022
```

#### 2. AWS部署
```bash
# 运行部署脚本
./deploy-to-aws.sh
```

### 📊 API端点

1. **年份数据**: `/api/map/data/{year}`
   - 示例: `http://54.166.219.154:5000/api/map/data/2022`

2. **地图边界**: `/api/map/geojson`
   - 示例: `http://54.166.219.154:5000/api/map/geojson`

3. **州时间序列**: `/api/chart/data/{state}`
   - 示例: `http://54.166.219.154:5000/api/chart/data/New%20South%20Wales`

### 🎯 部署架构

- **平台**: AWS ECS Fargate
- **容器**: Docker
- **数据库**: MySQL (RDS)
- **网络**: VPC + 公网IP
- **监控**: CloudWatch Logs

### 📝 注意事项

- 确保AWS CLI已配置
- 确保有足够的IAM权限
- 部署前请检查数据库连接配置

# TSX Trend API Docker Deployment Guide

## 📋 Overview

This project uses Docker to containerize a Flask application that can be deployed to AWS ECS or EC2.

## 🚀 Local Development

### 1. Using Docker Compose (Recommended)

```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Using Docker Directly

```bash
# Build image
docker build -t tsx-trend-api .

# Run container
docker run -p 5000:5000 tsx-trend-api

# Run in background
docker run -d -p 5000:5000 --name tsx-trend-api tsx-trend-api
```

## ☁️ AWS Deployment

### Method 1: Using Deployment Script (Recommended)

1. Ensure AWS CLI is installed and credentials are configured
2. Run deployment script:

```bash
chmod +x aws-deploy.sh
./aws-deploy.sh
```

### Method 2: Manual Deployment

#### 1. Build and Push to ECR

```bash
# Set variables
AWS_REGION="us-east-1"
ECR_REPOSITORY="plantx-tsx-trend-api"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Build image
docker build -t $ECR_REPOSITORY .

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag image
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

# Create ECR repository
aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

# Push image
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
```

#### 2. Deploy to ECS

1. Update account ID in `ecs-task-definition.json`
2. Register task definition:

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

3. Create ECS service or use existing service

## 🔧 Configuration

### Environment Variables

- `FLASK_ENV`: Set to `production` for production environment
- Database connection info is hardcoded, recommend using environment variables in production

### Ports

- Application runs on port 5000
- Container internal port: 5000
- External access port: 5000

## 📊 Health Checks

Application includes the following health check endpoints:

- `GET /api/map/geojson` - Basic health check
- `GET /api/map/data/{year}` - Year data
- `GET /api/chart/data/{state}` - State time series data

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database configuration
   - Ensure network connection is normal
   - Verify database credentials

2. **Port Conflict**
   - Change port mapping in docker-compose.yml
   - Or use `docker run -p other-port:5000`

3. **Insufficient Memory**
   - Increase memory allocation in ECS task definition
   - Or adjust Docker container memory limits

### View Logs

```bash
# Docker Compose
docker-compose logs -f

# Direct Docker
docker logs -f tsx-trend-api

# ECS
aws logs tail /ecs/plantx-tsx-trend-api --follow
```

## 📝 API Endpoints

- `GET /api/map/geojson` - Get map GeoJSON data
- `GET /api/map/data/{year}` - Get choropleth data for specified year
- `GET /api/chart/data/{state}` - Get time series data for specified state

## 🔒 Security Notes

1. Do not hardcode database passwords in production
2. Use AWS Secrets Manager or environment variables to store sensitive information
3. Configure appropriate IAM roles and permissions
4. Enable VPC and network security groups



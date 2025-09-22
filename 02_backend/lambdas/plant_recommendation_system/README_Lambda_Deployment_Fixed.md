# Lambda Function Deployment Instructions - Fixed Version

## Issue Resolution

✅ **Fixed Issues**:
- Removed pandas and numpy dependencies to avoid Windows DLL compatibility issues
- Used pure Python to implement data processing logic
- Optimized dependency package size (reduced from 50MB+ to 0.52MB)
- All dependencies have been locally tested and verified

## File Structure

```
03_plant_recommendation_system/
├── lambda_function.py              # Lambda function entry point
├── plant_recommendation_lambda.py  # Plant recommendation core logic (optimized version)
├── common/                         # Common utility modules
│   ├── __init__.py
│   ├── db_utils.py
│   ├── config.py
│   ├── http_utils.py
│   └── s3_utils.py
├── pymysql/                        # MySQL database driver
├── requests/                       # HTTP request library
├── urllib3/                        # HTTP library dependencies
├── certifi/                        # SSL certificate library
├── charset_normalizer/             # Character encoding detection
├── idna/                           # Internationalized domain name library
├── plant_recommendation_lambda.zip # Deployment package (0.52MB)
└── package_lambda.py               # Packaging script
```

## Deployment Steps

### 1. Using Pre-built Deployment Package

Directly use the created `plant_recommendation_lambda.zip` file:

1. Log in to AWS Console
2. Navigate to Lambda service
3. Create new function or update existing function
4. Upload `plant_recommendation_lambda.zip`
5. Set handler to: `lambda_function.lambda_handler`

### 2. Configure Environment Variables

Add the following environment variables in Lambda function configuration:

```
DB_HOST=your-database-host
DB_NAME=your-database-name
DB_USER=your-database-username
DB_PASSWORD=your-database-password
DB_PORT=3306
```

### 3. Configure Lambda Function Settings

- **Runtime**: Python 3.13
- **Architecture**: x86_64
- **Timeout**: 30 seconds
- **Memory**: 512MB (recommended)

### 4. Configure API Gateway

1. Create API Gateway
2. Create resources and methods
3. Integrate with Lambda function
4. Deploy API

## API Usage Instructions

### Request Format

**GET Request:**
```
GET /plants?lat=-37.8136&lon=144.9631
```

**POST Request:**
```json
{
    "latitude": -37.8136,
    "longitude": 144.9631
}
```

### Response Format

```json
{
    "success": true,
    "latitude": -37.8136,
    "longitude": 144.9631,
    "aggregated_weather": {
        "extreme_min_temp": 5.2,
        "extreme_max_temp": 28.4,
        "avg_sunshine_duration": 7.5,
        "avg_max_uv_index": 6.2,
        "avg_daily_precipitation": 2.1,
        "avg_relative_humidity": 65.3
    },
    "recommended_plant_ids": [1, 5, 12, 23, 45],
    "total_recommendations": 5
}
```

## Optimization Details

### 1. Dependency Optimization
- **Removed pandas/numpy**: Used pure Python to implement data processing
- **Retained core dependencies**: requests, urllib3, certifi, charset_normalizer, idna
- **File size**: Reduced from 50MB+ to 0.52MB

### 2. Performance Optimization
- **Cold start time**: Significantly reduced
- **Memory usage**: Lower memory consumption
- **Compatibility**: Fully compatible with AWS Lambda Linux environment

### 3. Functionality Maintained
- **Weather data retrieval**: Calls Open-Meteo API to get 16-day weather forecast
- **Plant data query**: Queries plant information from MySQL database
- **Intelligent matching**: Recommends suitable plants based on weather conditions
- **Random sorting**: Randomizes recommendation results to increase diversity

## Testing Verification

✅ **Local Testing Passed**:
- All dependencies imported successfully
- Weather API calls working normally
- Lambda handler structure correct

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependency files are in the ZIP package
2. **Database connection failure**: Check environment variable configuration
3. **Timeout errors**: Increase Lambda timeout duration
4. **Insufficient memory**: Increase Lambda memory configuration

### Repackaging

If repackaging is needed, run:
```bash
python package_lambda.py
```

## Important Notes

1. Ensure database connection configuration is correct
2. Lambda function timeout recommended to be set to 30 seconds
3. Memory configuration recommended to be set to 512MB or higher
4. Ensure VPC configuration is correct (if database is in VPC)
5. Deployment package size has been optimized, no S3 upload needed

---

**Deployment package is ready!** 🚀

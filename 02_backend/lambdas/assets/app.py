# lambdas/assets/app.py
from __future__ import annotations
import os
import json
from common import http_utils, s3_utils

BUCKET_NAME = os.environ.get("ASSETS_BUCKET")  # 记得在 Lambda 配置里加环境变量

def handler(event, context):
    """
    支持的路由：
    - GET /assets/download?key=xxx     -> 获取下载 URL
    - POST /assets/upload              -> 获取上传 URL（PUT 或 POST 方式）
    """
    route_key = event.get("routeKey") or ""
    method = event.get("requestContext", {}).get("http", {}).get("method")
    path = event.get("rawPath", "")

    try:
        # ---- 下载 URL ----
        if method == "GET" and path.startswith("/assets/download"):
            q = event.get("queryStringParameters") or {}
            key = q.get("key")
            if not key:
                return http_utils.bad_request({"message": "missing key"})
            url = s3_utils.generate_presigned_get_url(BUCKET_NAME, key, expires=900)
            return http_utils.ok({"download_url": url})

        # ---- 上传 URL ----
        if method == "POST" and path.startswith("/assets/upload"):
            body = http_utils.parse_json_body(event)
            filename = body.get("filename")
            if not filename:
                return http_utils.bad_request({"message": "missing filename"})

            key = f"uploads/{filename}"
            # 方案1: PUT 直传
            put_url = s3_utils.generate_presigned_put_url(BUCKET_NAME, key, expires=900)

            # 方案2: POST 表单上传（可选，支持限制大小）
            post_data = s3_utils.generate_presigned_post(BUCKET_NAME, "uploads/", expires=900)

            return http_utils.ok({
                "s3_key": key,
                "put_url": put_url,
                "post_data": post_data,
            })

        # 其他路由
        return http_utils.not_found({"message": f"No route for {method} {path}"})

    except Exception as e:
        return http_utils.server_error({"message": str(e)})

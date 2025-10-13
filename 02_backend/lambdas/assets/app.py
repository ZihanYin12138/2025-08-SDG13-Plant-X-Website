# lambdas/assets/app.py
from __future__ import annotations
import os
import json
from common import http_utils, s3_utils

BUCKET_NAME = os.environ.get("ASSETS_BUCKET")  # Remember to add environment variable in Lambda configuration

def handler(event, context):
    """
    Supported routes:
    - GET /assets/download?key=xxx     -> Get download URL
    - POST /assets/upload              -> Get upload URL (PUT or POST method)
    """
    route_key = event.get("routeKey") or ""
    method = event.get("requestContext", {}).get("http", {}).get("method")
    path = event.get("rawPath", "")

    try:
        # ---- Download URL ----
        if method == "GET" and path.startswith("/assets/download"):
            q = event.get("queryStringParameters") or {}
            key = q.get("key")
            if not key:
                return http_utils.bad_request({"message": "missing key"})
            url = s3_utils.generate_presigned_get_url(BUCKET_NAME, key, expires=900)
            return http_utils.ok({"download_url": url})

        # ---- Upload URL ----
        if method == "POST" and path.startswith("/assets/upload"):
            body = http_utils.parse_json_body(event)
            filename = body.get("filename")
            if not filename:
                return http_utils.bad_request({"message": "missing filename"})

            key = f"uploads/{filename}"
            # Option 1: PUT direct upload
            put_url = s3_utils.generate_presigned_put_url(BUCKET_NAME, key, expires=900)

            # Option 2: POST form upload (optional, supports size limits)
            post_data = s3_utils.generate_presigned_post(BUCKET_NAME, "uploads/", expires=900)

            return http_utils.ok({
                "s3_key": key,
                "put_url": put_url,
                "post_data": post_data,
            })

        # Other routes
        return http_utils.not_found({"message": f"No route for {method} {path}"})

    except Exception as e:
        return http_utils.server_error({"message": str(e)})

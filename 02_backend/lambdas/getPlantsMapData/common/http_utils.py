# common/http_utils.py
from __future__ import annotations
import json
from typing import Any, Dict, Optional

DEFAULT_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    # CORS（按需修改域名）
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Requested-With",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
}

def response(
    status: int,
    body: Any,
    headers: Optional[Dict[str, str]] = None,
    is_base64: bool = False,
) -> Dict[str, Any]:
    h = dict(DEFAULT_HEADERS)
    if headers:
        h.update(headers)
    if isinstance(body, (dict, list)):
        body_str = json.dumps(body, ensure_ascii=False)
    elif isinstance(body, str):
        body_str = body
    else:
        body_str = json.dumps(body, ensure_ascii=False)
    return {
        "statusCode": status,
        "headers": h,
        "isBase64Encoded": is_base64,
        "body": body_str,
    }

def ok(body: Any, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    return response(200, body, headers)

def created(body: Any, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    return response(201, body, headers)

def bad_request(body: Any, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    return response(400, body, headers)

def unauthorized(body: Any, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    return response(401, body, headers)

def forbidden(body: Any, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    return response(403, body, headers)

def not_found(body: Any, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    return response(404, body, headers)

def server_error(body: Any, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    return response(500, body, headers)

def parse_json_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse JSON body from API Gateway (HTTP API / REST) event safely."""
    body = event.get("body")
    if not body:
        return {}
    if event.get("isBase64Encoded"):
        # 按需处理二进制，这里假设不是二进制 JSON
        import base64
        body = base64.b64decode(body).decode("utf-8", errors="ignore")
    try:
        return json.loads(body)
    except Exception:
        return {}

def query_param(event: Dict[str, Any], key: str, default: Optional[str] = None) -> Optional[str]:
    q = event.get("queryStringParameters") or {}
    return q.get(key, default)

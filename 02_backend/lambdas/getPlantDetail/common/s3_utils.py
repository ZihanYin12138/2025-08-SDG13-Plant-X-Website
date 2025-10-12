# common/s3_utils.py
from __future__ import annotations
import json
import io
import mimetypes
import boto3
from typing import Any, Dict, Optional, Tuple

_s3 = boto3.client("s3")

def get_object_bytes(bucket: str, key: str) -> bytes:
    resp = _s3.get_object(Bucket=bucket, Key=key)
    return resp["Body"].read()

def put_object_bytes(bucket: str, key: str, data: bytes, content_type: Optional[str] = None) -> None:
    ct = content_type or mimetypes.guess_type(key)[0] or "application/octet-stream"
    _s3.put_object(Bucket=bucket, Key=key, Body=data, ContentType=ct)

def get_json(bucket: str, key: str) -> Any:
    raw = get_object_bytes(bucket, key)
    return json.loads(raw.decode("utf-8"))

def put_json(bucket: str, key: str, obj: Any) -> None:
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    put_object_bytes(bucket, key, data, content_type="application/json; charset=utf-8")

def generate_presigned_get_url(bucket: str, key: str, expires: int = 900) -> str:
    """A time-limited GET URL for direct browser download."""
    return _s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires,
    )

def generate_presigned_put_url(bucket: str, key: str, expires: int = 900, content_type: Optional[str] = None) -> str:
    """A time-limited PUT URL for browser direct upload."""
    params = {"Bucket": bucket, "Key": key}
    if content_type:
        params["ContentType"] = content_type
    return _s3.generate_presigned_url(
        ClientMethod="put_object",
        Params=params,
        ExpiresIn=expires,
    )

def generate_presigned_post(bucket: str, key_prefix: str, expires: int = 900, max_size_mb: int = 20) -> Dict[str, Any]:
    """Form-based browser upload (multipart). Returns dict with url & fields."""
    conditions = [
        ["starts-with", "$key", key_prefix],
        ["content-length-range", 1, max_size_mb * 1024 * 1024],
    ]
    return _s3.generate_presigned_post(
        Bucket=bucket,
        Key=f"{key_prefix}${{filename}}",
        Fields={},
        Conditions=conditions,
        ExpiresIn=expires,
    )

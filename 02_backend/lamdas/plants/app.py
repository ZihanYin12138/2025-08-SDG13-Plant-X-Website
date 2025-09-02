# lambdas/plants/app.py
from __future__ import annotations
from typing import Any, Dict

from common import (
    ok, bad_request, not_found, server_error,
    query_param,
    get_plant_by_general_id, search_plants_by_name, fetch_all
)

def _to_int(s: str | None, default: int) -> int:
    try:
        return int(s) if s is not None else default
    except Exception:
        return default

def handler(event: Dict[str, Any], context):
    """
    支持的请求方式：
    - GET /plants?general_plant_id=1         → 按 ID 精确查一条
    - GET /plants?q=maple&limit=20&offset=0  → 按名字模糊查（common_name / scientific_name）
    - GET /plants?limit=20&offset=0          → 列表（不带 q/id）
    """
    try:
        method = event.get("requestContext", {}).get("http", {}).get("method", "")
        path   = event.get("rawPath", "")

        if method != "GET" or not path.startswith("/plants"):
            return bad_request({"message": f"Unsupported route: {method} {path}"})

        # ---- 参数解析 ----
        gid    = query_param(event, "general_plant_id")
        q      = query_param(event, "q")
        limit  = _to_int(query_param(event, "limit"), 20)
        offset = _to_int(query_param(event, "offset"), 0)

        # ---- 按 ID 精确查 ----
        if gid:
            try:
                gid_int = int(gid)
            except ValueError:
                return bad_request({"message": "general_plant_id must be an integer"})
            row = get_plant_by_general_id(gid_int)
            if not row:
                return not_found({"message": "plant not found"})
            return ok(row)

        # ---- 按名字模糊搜索 ----
        if q:
            items = search_plants_by_name(q=q, limit=limit)
            return ok({"items": items, "limit": limit, "offset": offset})

        # ---- 默认：列表 ----
        items = fetch_all(
            "SELECT * FROM Table01_PlantMainTable ORDER BY plant_id ASC LIMIT %s OFFSET %s",
            (limit, offset)
        )
        return ok({"items": items, "limit": limit, "offset": offset})

    except Exception as e:
        return server_error({"message": f"internal error: {str(e)}"})

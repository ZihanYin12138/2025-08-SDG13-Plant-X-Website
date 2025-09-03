# lambdas/plants/app.py
from __future__ import annotations
import os, json
from typing import Any, Dict, List, Optional

from common import fetch_one, fetch_all

DEFAULT_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Requested-With",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
}

def _resp(status: int, body: Any):
    return {
        "statusCode": status,
        "headers": DEFAULT_HEADERS,
        "isBase64Encoded": False,
        "body": json.dumps(body, ensure_ascii=False),
    }

def _to_int(s: Optional[str], default: int) -> int:
    try:
        return int(s) if s is not None else default
    except Exception:
        return default

# -------- 关键适配：统一从事件中抽取 method/path/query ----------
def _extract_req(event: Dict[str, Any]) -> tuple[str, str, Dict[str, str]]:
    """
    返回 (method, path, queryStringParameters)
    - HTTP API v2: requestContext.http.method + rawPath
    - REST API v1: httpMethod + path
    """
    # v2
    rc = event.get("requestContext") or {}
    http_v2 = rc.get("http") or {}
    if http_v2.get("method") and event.get("rawPath"):
        return (
            http_v2.get("method", ""),
            event.get("rawPath", ""),
            event.get("queryStringParameters") or {},
        )
    # v1
    return (
        event.get("httpMethod", "") or "",
        event.get("path", "") or "",
        event.get("queryStringParameters") or {},
    )

# ---------- 搜索列表 ----------
def search_plants(q: str, limit: int, offset: int) -> Dict[str, Any]:
    like = f"%{q}%"

    # 总数
    cnt_row = fetch_one(
        """
        SELECT COUNT(*) AS cnt
        FROM Table01_PlantMainTable m
        WHERE (m.common_name LIKE %s OR m.scientific_name LIKE %s)
        """,
        (like, like),
    )
    total = int(cnt_row["cnt"]) if cnt_row else 0

    # 列表
    rows = fetch_all(
        """
        SELECT
          m.general_plant_id,
          m.common_name,
          m.scientific_name,
          COALESCE(MIN(img.thumbnail_image), MIN(img.regular_url_image)) AS image_url
        FROM Table01_PlantMainTable m
        LEFT JOIN Table05_GeneralPlantImageTable img
               ON img.general_plant_id = m.general_plant_id
        WHERE (m.common_name LIKE %s OR m.scientific_name LIKE %s)
        GROUP BY m.general_plant_id, m.common_name, m.scientific_name
        ORDER BY MIN(m.plant_id) ASC
        LIMIT %s OFFSET %s
        """,
        (like, like, limit, offset),
    )

    items = [
        {
            "general_plant_id": r["general_plant_id"],
            "common_name": r.get("common_name"),
            "scientific_name": r.get("scientific_name"),
            "image_url": r.get("image_url"),
        }
        for r in rows
    ]
    return {"items": items, "total": total, "limit": limit, "offset": offset}

# ---------- 详情 ----------
def get_plant_detail(gid: int) -> Optional[Dict[str, Any]]:
    base = fetch_one(
        """
        SELECT
            m.plant_id, m.general_plant_id, m.threatened_plant_id,
            m.common_name, m.scientific_name, m.other_name,
            m.if_threatened, m.if_edible, m.if_indoors, m.if_medicinal,
            m.if_poisonous, m.if_fruits, m.if_flowers,
            m.sun_expose, m.watering, m.plant_cycle, m.growth_rate
        FROM Table01_PlantMainTable m
        WHERE m.general_plant_id = %s
        """,
        (gid,),
    )
    if not base:
        return None

    desc = fetch_one(
        """
        SELECT *
        FROM Table02_GeneralPlantDescriptionTable
        WHERE general_plant_id = %s
        """,
        (gid,),
    )

    care = fetch_one(
        """
        SELECT *
        FROM Table03_GeneralPlantCareGuideTable
        WHERE general_plant_id = %s
        """,
        (gid,),
    )

    dist = fetch_one(
        """
        SELECT *
        FROM Table04_GeneralPlantDistributionMapTable
        WHERE general_plant_id = %s
        """,
        (gid,),
    )

    imgs = fetch_all(
        """
        SELECT general_plant_id, thumbnail_image, regular_url_image
        FROM Table05_GeneralPlantImageTable
        WHERE general_plant_id = %s
        """,
        (gid,),
    )
    image_urls: List[str] = []
    for r in imgs:
        for url in (r.get("thumbnail_image"), r.get("regular_url_image")):
            if url and url not in image_urls:
                image_urls.append(url)

    tpid = base.get("threatened_plant_id")
    threatened = None
    if tpid:
        t_desc = fetch_one(
            """
            SELECT *
            FROM Table06_ThreatenedPlantDescriptionTable
            WHERE threatened_plant_id = %s
            """,
            (tpid,),
        )
        t_care = fetch_one(
            """
            SELECT *
            FROM Table07_ThreatenedPlantCareGuideTable
            WHERE threatened_plant_id = %s
            """,
            (tpid,),
        )
        if t_desc or t_care:
            threatened = {"description": t_desc, "care_guide": t_care}

    detail = {
        **base,
        "description": desc,
        "care_guide": care,
        "distribution_map": dist,
        "image_urls": image_urls,
    }
    if threatened:
        detail["threatened"] = threatened
    return detail

# ---------- Lambda handler ----------
def handler(event, context):
    method, path, qs = _extract_req(event)

    # CORS 预检
    if method == "OPTIONS":
        return _resp(200, {"ok": True})

    try:
        if method != "GET" or not str(path).startswith("/plants"):
            return _resp(400, {"message": f"Unsupported route: {method} {path}"})

        gid_param = (qs or {}).get("general_plant_id")
        q = (qs or {}).get("q")
        limit = _to_int((qs or {}).get("limit"), 20)
        offset = _to_int((qs or {}).get("offset"), 0)

        if gid_param:
            try:
                gid = int(gid_param)
            except ValueError:
                return _resp(400, {"message": "general_plant_id must be an integer"})
            data = get_plant_detail(gid)
            if not data:
                return _resp(404, {"message": "plant not found"})
            return _resp(200, data)

        if q:
            return _resp(200, search_plants(q=q, limit=limit, offset=offset))

        return _resp(400, {"message": "Missing query. Use ?q=keyword or ?general_plant_id=ID"})

    except Exception as e:
        return _resp(500, {"message": f"internal error: {str(e)}"})

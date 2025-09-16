from __future__ import annotations
import json
from typing import Any, Dict, List, Optional

# Reuse your shared DB helpers
from common import fetch_all

# ---------- HTTP helpers ----------
DEFAULT_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Requested-With",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
}

def _resp(status: int, body: Any):
    return {
        "statusCode": status,
        "headers": DEFAULT_HEADERS,
        "isBase64Encoded": False,
        "body": json.dumps(body, ensure_ascii=False),
    }

# ---------- Request parsing (supports API Gateway REST v1 & HTTP v2) ----------

def _extract_req(event: Dict[str, Any]) -> tuple[str, Dict[str, str]]:
    rc = event.get("requestContext") or {}
    http_v2 = rc.get("http") or {}
    if http_v2.get("method"):
        return http_v2.get("method", "GET"), (event.get("queryStringParameters") or {})
    return (event.get("httpMethod", "GET") or "GET"), (event.get("queryStringParameters") or {})


def _to_int(s: Optional[str], default: int) -> int:
    try:
        return int(s) if s is not None else default
    except Exception:
        return default

# ---------- Core: single-SQL fuzzy search on Table09.common_name ----------
# Returns: all columns from Table09 + aggregated regular_url_image from Table10

SQL = (
    """
    SELECT
      d.plant_disease_id,
      d.common_name,
      d.scientific_name,
      d.other_name,
      d.host,
      d.description,
      d.solution,
      -- Aggregate all regular_url_image in one pass
      GROUP_CONCAT(DISTINCT i.regular_url_image ORDER BY i.regular_url_image SEPARATOR '\n') AS regular_url_images
    FROM Table09_PlantDiseaseTable AS d
    LEFT JOIN Table10_PlantDiseaseImageTable AS i
      ON i.plant_disease_id = d.plant_disease_id
    WHERE d.common_name LIKE %s
    GROUP BY
      d.plant_disease_id,
      d.common_name,
      d.scientific_name,
      d.other_name,
      d.host,
      d.description,
      d.solution
    ORDER BY d.plant_disease_id ASC
    LIMIT %s OFFSET %s
    """
)


def search_by_common_name(common_name_keyword: str, limit: int, offset: int) -> Dict[str, Any]:
    like = f"%{common_name_keyword}%"
    rows = fetch_all(SQL, (like, limit, offset))

    items: List[Dict[str, Any]] = []
    for r in rows:
        # Split GROUP_CONCAT into a list; filter empty/None
        imgs = []
        if r.get("regular_url_images"):
            imgs = [u for u in str(r["regular_url_images"]).split("\n") if u]
        item = {
            "plant_disease_id": r.get("plant_disease_id"),
            "common_name": r.get("common_name"),
            "scientific_name": r.get("scientific_name"),
            "other_name": r.get("other_name"),  # JSON/text per schema
            "host": r.get("host"),              # JSON/text per schema
            "description": r.get("description"),
            "solution": r.get("solution"),
            "regular_url_images": imgs,
        }
        items.append(item)

    return {"items": items, "limit": limit, "offset": offset}


# ---------- Lambda entry ----------

def handler(event, context):
    method, qs = _extract_req(event)

    if method == "OPTIONS":
        return _resp(200, {"ok": True})

    if method != "GET":
        return _resp(405, {"message": "Only GET is supported for this function"})

    q = (qs.get("q") or qs.get("common_name") or "").strip()
    if not q:
        return _resp(400, {"message": "Missing query. Use ?q=keyword (fuzzy match on common_name)"})

    limit = _to_int(qs.get("limit"), 20)
    offset = _to_int(qs.get("offset"), 0)

    try:
        data = search_by_common_name(q, limit, offset)
        return _resp(200, data)
    except Exception as e:
        # Return lightweight error (avoid leaking internals)
        return _resp(500, {"message": f"internal error: {e}"})

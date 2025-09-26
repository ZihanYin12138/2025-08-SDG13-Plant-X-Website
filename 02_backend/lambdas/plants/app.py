# lambdas/plants/app.py
from __future__ import annotations
import os, json
from typing import Any, Dict, List, Optional, Tuple

from common import fetch_one, fetch_all

# ===== After import, add this section: table name and existence check =====
THREAT_IMG_TABLE = os.environ.get("THREAT_IMG_TABLE", "Table08_ThreatenedPlantImageTable")
_TABLE_EXISTS_CACHE: Dict[str, bool] = {}

def _table_exists(table_name: str) -> bool:
    if table_name in _TABLE_EXISTS_CACHE:
        return _TABLE_EXISTS_CACHE[table_name]
    row = fetch_one(
        "SELECT 1 AS ok FROM information_schema.tables "
        "WHERE table_schema = DATABASE() AND table_name = %s",
        (table_name,),
    )
    ok = bool(row)
    _TABLE_EXISTS_CACHE[table_name] = ok
    return ok


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

# -------- Unified extraction of method/path/query from event ----------
def _extract_req(event: Dict[str, Any]) -> tuple[str, str, Dict[str, str]]:
    """Return (method, path, queryStringParameters); compatible with HTTP API v2 / REST v1."""
    rc = event.get("requestContext") or {}
    http_v2 = rc.get("http") or {}
    if http_v2.get("method") and event.get("rawPath"):
        return (
            http_v2.get("method", ""),
            event.get("rawPath", ""),
            event.get("queryStringParameters") or {},
        )
    return (
        event.get("httpMethod", "") or "",
        event.get("path", "") or "",
        event.get("queryStringParameters") or {},
    )

# ---------- Boolean filters (7 types) ----------
_FILTER_KEYS = [
    "if_threatened",
    "if_edible",
    "if_indoors",
    "if_medicinal",
    "if_poisonous",
    "if_fruits",
    "if_flowers",
]

def _to_bool(val: Optional[str]) -> Optional[bool]:
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in {"1", "true", "t", "yes", "y"}:
        return True
    if s in {"0", "false", "f", "no", "n"}:
        return False
    return None

def _bool_clause(col: str, desired: bool) -> str:
    """
    Compatible with BOOLEAN/TEXT: convert column to string for lower case comparison;
    True matches {'true','1'}, False matches {'false','0'}.
    """
    if desired:
        return f"(LOWER(CAST({col} AS CHAR)) IN ('true','1'))"
    else:
        return f"(LOWER(CAST({col} AS CHAR)) IN ('false','0'))"

# ---------- New 4 enum/list filters ----------
_WATERING_SET = {"frequent", "average", "minimal"}
_GROWTH_SET = {"high", "moderate", "low"}

def _norm_watering(v: Optional[str]) -> Optional[str]:
    if not v: return None
    s = v.strip().lower()
    return s if s in _WATERING_SET else None

def _norm_growth(v: Optional[str]) -> Optional[str]:
    if not v: return None
    s = v.strip().lower()
    return s if s in _GROWTH_SET else None

def _norm_cycle(v: Optional[str]) -> Optional[str]:
    if not v: return None
    s = v.strip().lower()
    mapping = {
        "every year": "Every year",
        "once a year": "Once a year",
        "every 2 years": "Every 2 years",
        "every2years": "Every 2 years",
        "every-2-years": "Every 2 years",
    }
    return mapping.get(s, None)

_SUN_ALLOWED = {
    "full shade",
    "part shade",
    "part sun/part shade",
    "full sun",
}
def _norm_sun_list(v: Optional[str]) -> List[str]:
    if not v: return []
    parts = [p.strip().lower() for p in v.split(",") if p.strip()]
    return [p for p in parts if p in _SUN_ALLOWED]

# ---------- Build WHERE clause (keyword + 7 boolean + 4 new filters) ----------
def _build_where_and_params(
    q: Optional[str],
    bool_filters: Dict[str, bool],
    watering: Optional[str],
    plant_cycle: Optional[str],
    growth_rate: Optional[str],
    sun_list: List[str],
) -> Tuple[str, List[Any]]:
    clauses: List[str] = []
    params: List[Any] = []

    if q:
        like = f"%{q}%"
        clauses.append("(m.common_name LIKE %s OR m.scientific_name LIKE %s)")
        params += [like, like]

    # 7 boolean filters
    for k, v in bool_filters.items():
        clauses.append(_bool_clause(f"m.{k}", v))

    # 3 enum filters
    if watering:
        clauses.append("LOWER(m.watering) = %s")
        params.append(watering)  # already lowercase
    if plant_cycle:
        clauses.append("LOWER(m.plant_cycle) = LOWER(%s)")
        params.append(plant_cycle)  # normalized original word
    if growth_rate:
        clauses.append("LOWER(m.growth_rate) = %s")
        params.append(growth_rate)  # already lowercase

    # sun_expose: match any one
    if sun_list:
        or_parts = []
        for _ in sun_list:
            or_parts.append(
                "COALESCE(JSON_CONTAINS(CAST(m.sun_expose AS JSON), JSON_QUOTE(%s), '$'), 0) = 1"
            )
        clauses.append("(" + " OR ".join(or_parts) + ")")
        params.extend(sun_list)

    where_sql = " AND ".join(clauses) if clauses else "1=1"
    return where_sql, params

# ---------- Search list ----------
# ---------- Search list (replace entire function) ----------
def search_plants(
    q: Optional[str],
    limit: int,
    offset: int,
    bool_filters: Dict[str, bool],
    watering: Optional[str],
    plant_cycle: Optional[str],
    growth_rate: Optional[str],
    sun_list: List[str],
) -> Dict[str, Any]:
    where_sql, params = _build_where_and_params(
        q, bool_filters, watering, plant_cycle, growth_rate, sun_list
    )

    # Whether to filter by threatened status
    use_threat = bool_filters.get("if_threatened") is True
    threat_img_ok = _table_exists(THREAT_IMG_TABLE)

    # Count total
    cnt_row = fetch_one(
        f"SELECT COUNT(*) AS cnt FROM Table01_PlantMainTable m WHERE {where_sql}",
        tuple(params),
    )
    total = int(cnt_row["cnt"]) if cnt_row else 0

    # Choose image join table
    if use_threat and threat_img_ok:
        join_sql = f"""
            LEFT JOIN `{THREAT_IMG_TABLE}` img
                   ON img.threatened_plant_id = m.threatened_plant_id
        """
    else:
        join_sql = """
            LEFT JOIN Table05_GeneralPlantImageTable img
                   ON img.general_plant_id = m.general_plant_id
        """

    # Note: when use_threat=true, also query threatened_plant_id
    rows = fetch_all(
        f"""
        SELECT
          m.general_plant_id,
          m.threatened_plant_id,
          m.common_name,
          m.scientific_name,
          COALESCE(MIN(img.thumbnail_image), MIN(img.regular_url_image)) AS image_url
        FROM Table01_PlantMainTable m
        {join_sql}
        WHERE {where_sql}
        GROUP BY m.general_plant_id, m.threatened_plant_id, m.common_name, m.scientific_name
        ORDER BY MIN(m.plant_id) ASC
        LIMIT %s OFFSET %s
        """,
        tuple(params + [limit, offset]),
    )

    items: List[Dict[str, Any]] = []
    for r in rows:
        if use_threat:
            items.append({
                "id_type": "threatened",
                "threatened_plant_id": r.get("threatened_plant_id"),
                "common_name": r.get("common_name"),
                "scientific_name": r.get("scientific_name"),
                "image_url": r.get("image_url"),
            })
        else:
            items.append({
                "id_type": "general",
                "general_plant_id": r["general_plant_id"],
                "common_name": r.get("common_name"),
                "scientific_name": r.get("scientific_name"),
                "image_url": r.get("image_url"),
            })

    return {"items": items, "total": total, "limit": limit, "offset": offset}


# ---------- Details ----------
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

# ---------- New: Threatened details ----------
def get_threatened_detail(tid: int) -> Optional[Dict[str, Any]]:
    """Return details based on threatened_plant_id: main table basic info + table06/07 + table08 images"""
    # First find a plant with this threatened_plant_id from the main table to get common fields like names
    base = fetch_one(
        """
        SELECT
            m.plant_id, m.general_plant_id, m.threatened_plant_id,
            m.common_name, m.scientific_name, m.other_name,
            m.if_threatened, m.if_edible, m.if_indoors, m.if_medicinal,
            m.if_poisonous, m.if_fruits, m.if_flowers,
            m.sun_expose, m.watering, m.plant_cycle, m.growth_rate
        FROM Table01_PlantMainTable m
        WHERE m.threatened_plant_id = %s
        LIMIT 1
        """,
        (tid,),
    )
    if not base:
        # No main table mapping, could also return only threatened table data; here choose to return 404 directly
        return None

    # Table06: Description
    t_desc = fetch_one(
        """
        SELECT *
        FROM Table06_ThreatenedPlantDescriptionTable
        WHERE threatened_plant_id = %s
        """,
        (tid,),
    )
    # Table07: Care
    t_care = fetch_one(
        """
        SELECT *
        FROM Table07_ThreatenedPlantCareGuideTable
        WHERE threatened_plant_id = %s
        """,
        (tid,),
    )
    # Table08: Images (if table exists)
    image_urls: List[str] = []
    if _table_exists(THREAT_IMG_TABLE):
        t_imgs = fetch_all(
            f"""
            SELECT threatened_plant_id, thumbnail_image, regular_url_image
            FROM `{THREAT_IMG_TABLE}`
            WHERE threatened_plant_id = %s
            """,
            (tid,),
        )
        for r in t_imgs:
            for url in (r.get("thumbnail_image"), r.get("regular_url_image")):
                if url and url not in image_urls:
                    image_urls.append(url)

    detail = {
        **base,
        "id_type": "threatened",
        "threatened": {
            "description": t_desc,
            "care_guide": t_care,
        },
        "image_urls": image_urls,
    }
    return detail


# ---------- Lambda handler ----------
# ---------- handler (only change "parameter parsing & routing" these lines) ----------
def handler(event, context):
    method, path, qs = _extract_req(event)

    if method == "OPTIONS":
        return _resp(200, {"ok": True})

    try:
        if method != "GET" or not str(path).startswith("/plants"):
            return _resp(400, {"message": f"Unsupported route: {method} {path}"})

        qs = qs or {}
        gid_param = qs.get("general_plant_id")
        tid_param = qs.get("threatened_plant_id")  # if you support threatened details
        q = qs.get("q")
        limit = _to_int(qs.get("limit"), 20)
        offset = _to_int(qs.get("offset"), 0)

        # ✅ Must initialize these first before entering any if branches
        bool_filters: Dict[str, bool] = {}
        for k in _FILTER_KEYS:
            b = _to_bool(qs.get(k))
            if b is not None:
                bool_filters[k] = b

        watering = _norm_watering(qs.get("watering"))
        plant_cycle = _norm_cycle(qs.get("plant_cycle"))
        growth_rate = _norm_growth(qs.get("growth_rate"))
        sun_list = _norm_sun_list(qs.get("sun_expose"))

        # (Details and list logic to be written later...)

        # ……(Boolean filtering and new filter parsing remain unchanged)……

        # Details 1: by threatened_plant_id
        if tid_param:
            try:
                tid = int(tid_param)
            except ValueError:
                return _resp(400, {"message": "threatened_plant_id must be an integer"})
            data = get_threatened_detail(tid)
            if not data:
                return _resp(404, {"message": "threatened plant not found"})
            return _resp(200, data)

        # Details 2: by general_plant_id
        if gid_param:
            try:
                gid = int(gid_param)
            except ValueError:
                return _resp(400, {"message": "general_plant_id must be an integer"})
            data = get_plant_detail(gid)
            if not data:
                return _resp(404, {"message": "plant not found"})
            return _resp(200, data)

        # List: supports keywords/filters
        if q or bool_filters or watering or plant_cycle or growth_rate or sun_list:
            data = search_plants(
                q=q,
                limit=limit,
                offset=offset,
                bool_filters=bool_filters,
                watering=watering,
                plant_cycle=plant_cycle,
                growth_rate=growth_rate,
                sun_list=sun_list,
            )
            return _resp(200, data)

        return _resp(400, {"message": "Missing query. Use ?q=keyword or ?general_plant_id=ID or ?threatened_plant_id=ID or filters"})
    except Exception as e:
        return _resp(500, {"message": f"internal error: {str(e)}"})


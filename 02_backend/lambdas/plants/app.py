# lambdas/plants/app.py
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from common import (
    ok, bad_request, not_found, server_error, query_param,
    fetch_one, fetch_all
)

# ---------- 小工具 ----------
def _to_int(s: Optional[str], default: int) -> int:
    try:
        return int(s) if s is not None else default
    except Exception:
        return default

def _escape_like(s: str) -> str:
    # 避免用户输入中的 %/_ 被当通配符
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

# ---------- 搜索：根据名字模糊 + 返回 ID/名字/图片 ----------
def search_plants(q: str, limit: int, offset: int) -> Dict[str, Any]:
    like = f"%{_escape_like(q)}%"

    # 统计总数
    cnt_row = fetch_one(
        """
        SELECT COUNT(*) AS cnt
        FROM Table01_PlantMainTable m
        WHERE (m.common_name LIKE %s ESCAPE '\\' OR m.scientific_name LIKE %s ESCAPE '\\')
        """,
        (like, like),
    )
    total = int(cnt_row["cnt"]) if cnt_row else 0

    # 取列表（连到图片表，优先缩略图，否则 regular）
    rows = fetch_all(
        """
        SELECT
            m.general_plant_id,
            m.common_name,
            m.scientific_name,
            COALESCE(img.thumbnail_image, img.regular_url_image) AS image_url
        FROM Table01_PlantMainTable m
        LEFT JOIN Table05_GeneralPlantImageTable img
               ON img.general_plant_id = m.general_plant_id
        WHERE (m.common_name LIKE %s ESCAPE '\\' OR m.scientific_name LIKE %s ESCAPE '\\')
        ORDER BY m.plant_id ASC
        LIMIT %s OFFSET %s
        """,
        (like, like, limit, offset),
    )

    # 仅返回列表页需要的轻量字段
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

# ---------- 详情：根据 ID 汇总多个表 ----------
def get_plant_detail(gid: int) -> Optional[Dict[str, Any]]:
    # 主表（基本标签）
    base = fetch_one(
        """
        SELECT
            m.plant_id,
            m.general_plant_id,
            m.threatened_plant_id,
            m.common_name,
            m.scientific_name,
            m.other_name,
            m.if_threatened,
            m.if_edible, m.if_indoors, m.if_medicinal, m.if_poisonous, m.if_fruits, m.if_flowers,
            m.sun_expose, m.watering, m.plant_cycle, m.growth_rate
        FROM Table01_PlantMainTable m
        WHERE m.general_plant_id = %s
        """,
        (gid,),
    )
    if not base:
        return None

    # 描述表
    desc = fetch_one(
        """
        SELECT
            general_plant_id,
            if_edible, if_indoors, if_medicinal, if_poisonous, if_fruits, if_flowers,
            plant_type, plant_cycle,
            attracts, propagation, description
        FROM Table02_GeneralPlantDescriptionTable
        WHERE general_plant_id = %s
        """,
        (gid,),
    )

    # 护理指南
    care = fetch_one(
        """
        SELECT
            general_plant_id,
            watering, watering_general_benchmark, sunlight, soil,
            drought_tolerant, salt_tolerant,
            pruning_month, pruning_count, pest_susceptibility,
            flowers_detail, harvest_season, growth_rate,
            maintenance, care_level,
            watering_guide, sunlight_guide, pruning_guide
        FROM Table03_GeneralPlantCareGuideTable
        WHERE general_plant_id = %s
        """,
        (gid,),
    )

    # 分布地图（如果有）
    dist = fetch_one(
        """
        SELECT general_plant_id, distribution_map_html
        FROM Table04_GeneralPlantDistributionMapTable
        WHERE general_plant_id = %s
        """,
        (gid,),
    )

    # 图片（缩略 + 正常）
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
        # 一行里可能有两列 URL，去重收集
        for url in [r.get("thumbnail_image"), r.get("regular_url_image")]:
            if url and url not in image_urls:
                image_urls.append(url)

    # 受威胁植物（若主表有 threatened_plant_id）
    threatened_detail = None
    threatened_care = None
    tpid = base.get("threatened_plant_id")
    if tpid:
        threatened_detail = fetch_one(
            """
            SELECT
              threatened_plant_id, conservation_status, provenance, weed_rating, habit,
              germplasm_source, conservation_benefit, local_benefits_description, horticultural_potential
            FROM Table06_ThreatenedPlantDescriptionTable
            WHERE threatened_plant_id = %s
            """,
            (tpid,),
        )
        threatened_care = fetch_one(
            """
            SELECT threatened_plant_id, soil, sun, propagation_methods, propagation_level, cultivation_note
            FROM Table07_ThreatenedPlantCareGuideTable
            WHERE threatened_plant_id = %s
            """,
            (tpid,),
        )

    # 组装详情
    detail: Dict[str, Any] = {
        **base,
        "description": desc,
        "care_guide": care,
        "distribution_map": dist,
        "image_urls": image_urls,
    }
    if threatened_detail or threatened_care:
        detail["threatened"] = {
            "description": threatened_detail,
            "care_guide": threatened_care,
        }
    return detail

# ---------- Lambda 入口 ----------
def handler(event: Dict[str, Any], context):
    """
    两个功能：
    1) 搜索列表：GET /plants?q=xxx&limit=20&offset=0
       -> 返回 { items: [{general_plant_id, common_name, scientific_name, image_url}], total, limit, offset }
    2) 详情页：  GET /plants?general_plant_id=123
       -> 返回合并后的详情对象（含多张表 & 图片列表）
    """
    try:
        method = event.get("requestContext", {}).get("http", {}).get("method", "")
        path   = event.get("rawPath", "")

        if method != "GET" or not path.startswith("/plants"):
            return bad_request({"message": f"Unsupported route: {method} {path}"})

        gid_param = query_param(event, "general_plant_id")
        q         = query_param(event, "q")
        limit     = _to_int(query_param(event, "limit"), 20)
        offset    = _to_int(query_param(event, "offset"), 0)

        # 详情：按 ID
        if gid_param:
            try:
                gid = int(gid_param)
            except ValueError:
                return bad_request({"message": "general_plant_id must be an integer"})
            detail = get_plant_detail(gid)
            if not detail:
                return not_found({"message": "plant not found"})
            return ok(detail)

        # 列表：按名字模糊
        if q:
            return ok(search_plants(q=q, limit=limit, offset=offset))

        # 没参数时，给个空提示或默认列表
        return bad_request({"message": "Missing query. Use ?q=keyword or ?general_plant_id=ID"})

    except Exception as e:
        return server_error({"message": f"internal error: {str(e)}"})

# common/db_utils.py  —— pymysql 实现（与现有 API 兼容）
from __future__ import annotations
import json
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pymysql
from pymysql.cursors import DictCursor

# ---- 环境变量（与现有保持一致）----
DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ.get("DB_PASSWORD") or os.environ.get("DB_PASS")
DB_NAME = os.environ["DB_NAME"]
DB_PORT = int(os.environ.get("DB_PORT", "3306"))

# ---- 全局连接（冷启动后复用）----
_conn: Optional[pymysql.connections.Connection] = None

def get_connection() -> pymysql.connections.Connection:
    """获取可复用 MySQL 连接；断开时自动重连。"""
    global _conn
    if _conn is None:
        _conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            autocommit=True,
            connect_timeout=10,
            cursorclass=DictCursor,   # 直接返回 dict，便于转 JSON
        )
        return _conn
    try:
        _conn.ping(reconnect=True)
    except Exception:
        _conn = None
        return get_connection()
    return _conn

def _maybe_parse_json(val: Any) -> Any:
    if isinstance(val, str):
        s = val.strip()
        if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
            try:
                return json.loads(s)
            except Exception:
                return val
    return val

def _postprocess_row(row: Dict[str, Any]) -> Dict[str, Any]:
    # 可按需自动解析潜在 JSON 字段
    return {k: _maybe_parse_json(v) for k, v in row.items()}

def fetch_all(sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        rows = cur.fetchall() or []
        return [_postprocess_row(r) for r in rows]

def fetch_one(sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        row = cur.fetchone()
        return _postprocess_row(row) if row else None

def execute(sql: str, params: Optional[Tuple[Any, ...]] = None) -> int:
    """执行 DML（INSERT/UPDATE/DELETE），返回受影响行数。"""
    conn = get_connection()
    with conn.cursor() as cur:
        affected = cur.execute(sql, params or ())
        return int(affected or 0)

def executemany(sql: str, seq_params: Iterable[Tuple[Any, ...]]) -> int:
    conn = get_connection()
    with conn.cursor() as cur:
        affected = cur.executemany(sql, list(seq_params))
        return int(affected or 0)

# ---- 示例业务函数（保持不变）----
def get_plant_by_general_id(gid: int) -> Optional[Dict[str, Any]]:
    return fetch_one(
        "SELECT * FROM Table01_PlantMainTable WHERE general_plant_id = %s",
        (gid,),
    )

def search_plants_by_name(q: str, limit: int = 20) -> List[Dict[str, Any]]:
    # 简单版：LIKE 模糊（如果想加转义/分页请在 handler 里处理）
    like = f"%{q}%"
    return fetch_all(
        "SELECT * FROM Table01_PlantMainTable "
        "WHERE common_name LIKE %s OR scientific_name LIKE %s "
        "LIMIT %s",
        (like, like, limit),
    )

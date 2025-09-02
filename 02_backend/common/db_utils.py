# common/db_utils.py
from __future__ import annotations
import json
import pymysql
from typing import Any, Dict, Iterable, List, Optional, Tuple
from .config import env_str, env_int

# 环境变量配置（支持 RDS Proxy）
DB_HOST = env_str("DB_HOST", required=True)
DB_USER = env_str("DB_USER", required=True)
DB_PASSWORD = env_str("DB_PASSWORD") or env_str("DB_PASS", required=True)
DB_NAME = env_str("DB_NAME", required=True)
DB_PORT = env_int("DB_PORT", "3306")

# 连接复用（冷启动后缓存）
_conn: Optional[pymysql.connections.Connection] = None

def get_connection() -> pymysql.connections.Connection:
    """Get a reusable MySQL connection (auto-reconnect)."""
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
            cursorclass=pymysql.cursors.DictCursor,
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

def fetch_all(sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        return [_postprocess_row(r) for r in rows]

def fetch_one(sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        row = cur.fetchone()
        return _postprocess_row(row) if row else None

def execute(sql: str, params: Optional[Tuple[Any, ...]] = None) -> int:
    """Execute DML (INSERT/UPDATE/DELETE). Returns affected rows."""
    conn = get_connection()
    with conn.cursor() as cur:
        affected = cur.execute(sql, params or ())
        return int(affected)

def executemany(sql: str, seq_params: Iterable[Tuple[Any, ...]]) -> int:
    conn = get_connection()
    with conn.cursor() as cur:
        affected = cur.executemany(sql, seq_params)
        return int(affected)

def _postprocess_row(row: Dict[str, Any]) -> Dict[str, Any]:
    # 可按需对潜在 JSON 字段做自动解析
    out = {}
    for k, v in row.items():
        out[k] = _maybe_parse_json(v)
    return out

# ---- 示例业务函数（可直接在 handler 里调用） ----
def get_plant_by_general_id(gid: int) -> Optional[Dict[str, Any]]:
    return fetch_one(
        "SELECT * FROM Table01_PlantMainTable WHERE general_plant_id = %s",
        (gid,),
    )

def search_plants_by_name(q: str, limit: int = 20) -> List[Dict[str, Any]]:
    like = f"%{q}%"
    return fetch_all(
        "SELECT * FROM Table01_PlantMainTable "
        "WHERE common_name LIKE %s OR scientific_name LIKE %s "
        "LIMIT %s",
        (like, like, limit),
    )

# common/db_utils.py
from __future__ import annotations
import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

import mysql.connector
from mysql.connector import Error

from .config import env_str, env_int

# -----------------------------
# 环境变量（把同事给你的配置填到 Lambda 环境变量里）
# 例：
#   DB_HOST=database-plantx.cqz06uycysiz.us-east-1.rds.amazonaws.com
#   DB_USER=zihan
#   DB_PASSWORD=********
#   DB_NAME=FIT5120_PlantX_Database
#   DB_PORT=3306
# -----------------------------
DB_HOST = env_str("DB_HOST", required=True)
DB_USER = env_str("DB_USER", required=True)
DB_PASSWORD = env_str("DB_PASSWORD") or env_str("DB_PASS", required=True)
DB_NAME = env_str("DB_NAME", required=True)
DB_PORT = env_int("DB_PORT", "3306")

# 可按需暴露开关（与同事给的配置对齐）
# mysql-connector 的 Python 版选项
ALLOW_LOCAL_INFILE = True     # 同事给的 allow_local_infile=True
USE_PURE = True               # 同事给的 use_pure=True

# 连接复用（冷启动后缓存）
_conn: Optional[mysql.connector.connection.MySQLConnection] = None

def get_connection() -> mysql.connector.connection.MySQLConnection:
    """
    获取可复用的 MySQL 连接；若断开则自动重连。
    注意：在高并发下更推荐使用 RDS Proxy 或 mysql.connector.pooling 连接池。
    """
    global _conn
    try:
        if _conn is None or not _conn.is_connected():
            _conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
                allow_local_infile=ALLOW_LOCAL_INFILE,
                use_pure=USE_PURE,
                autocommit=True,   # 保持与之前行为一致
            )
        return _conn
    except Error as e:
        _conn = None
        raise e

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
    # 可按需对潜在 JSON 字段做自动解析
    out = {}
    for k, v in row.items():
        out[k] = _maybe_parse_json(v)
    return out

def fetch_all(sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params or ())
        rows = cur.fetchall() or []
        return [_postprocess_row(r) for r in rows]
    finally:
        cur.close()

def fetch_one(sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params or ())
        row = cur.fetchone()
        return _postprocess_row(row) if row else None
    finally:
        cur.close()

def execute(sql: str, params: Optional[Tuple[Any, ...]] = None) -> int:
    """
    执行 DML（INSERT/UPDATE/DELETE），返回受影响行数。
    autocommit=True 已开启；若你想手动事务，可把 autocommit 关掉并在这里 commit/rollback。
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, params or ())
        return int(cur.rowcount or 0)
    finally:
        cur.close()

def executemany(sql: str, seq_params: Iterable[Tuple[Any, ...]]) -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.executemany(sql, list(seq_params))
        return int(cur.rowcount or 0)
    finally:
        cur.close()

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

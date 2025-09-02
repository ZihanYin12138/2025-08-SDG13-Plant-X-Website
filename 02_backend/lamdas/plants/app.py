# lambdas/plants/app.py
from __future__ import annotations
import mysql.connector
from mysql.connector import Error
from typing import Any, Dict, Optional

from common import (
    ok, bad_request, not_found, server_error,
    query_param
)

# ---- 数据库连接配置 ----
db_config = {
    'host': 'database-plantx.cqz06uycysiz.us-east-1.rds.amazonaws.com',
    'user': 'zihan',
    'password': '2002317Yzh12138.',
    'database': 'FIT5120_PlantX_Database',
    'allow_local_infile': True,
    'use_pure': True
}

_conn: Optional[mysql.connector.connection.MySQLConnection] = None

def get_connection():
    """获取可复用的 MySQL 连接"""
    global _conn
    try:
        if _conn is None or not _conn.is_connected():
            _conn = mysql.connector.connect(**db_config)
        return _conn
    except Error as e:
        _conn = None
        raise e

def fetch_one(sql: str, params: tuple) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    return row

def fetch_all(sql: str, params: tuple = ()) -> list[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return rows

# ---- Lambda 入口 ----
def handler(event: Dict[str, Any], context):
    """
    - GET /plants?general_plant_id=1  -> 查单条
    - GET /plants?q=maple&limit=20    -> 模糊查
    """
    try:
        method = event.get("requestContext", {}).get("http", {}).get("method", "")
        path   = event.get("rawPath", "")

        if method != "GET" or not path.startswith("/plants"):
            return bad_request({"message": f"Unsupported route: {method} {path}"})

        gid   = query_param(event, "general_plant_id")
        q     = query_param(event, "q")
        limit = int(query_param(event, "limit", "20"))

        # ---- 按 ID 查 ----
        if gid:
            row = fetch_one(
                "SELECT * FROM Table01_PlantMainTable WHERE general_plant_id = %s",
                (int(gid),)
            )
            if not row:
                return not_found({"message": "plant not found"})
            return ok(row)

        # ---- 按关键字模糊查 ----
        if q:
            like = f"%{q}%"
            items = fetch_all(
                "SELECT * FROM Table01_PlantMainTable "
                "WHERE common_name LIKE %s OR scientific_name LIKE %s "
                "LIMIT %s",
                (like, like, limit)
            )
            return ok({"items": items, "limit": limit})

        # ---- 默认列出前 N 条 ----
        items = fetch_all(
            "SELECT * FROM Table01_PlantMainTable ORDER BY plant_id ASC LIMIT %s",
            (limit,)
        )
        return ok({"items": items, "limit": limit})

    except Exception as e:
        return server_error({"message": f"internal error: {str(e)}"})

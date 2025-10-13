# common/__init__.py
"""
Common utilities package for AWS Lambda functions.
Exposes frequently used helpers for:
- HTTP response formatting
- Environment variable handling
- Database utilities
- S3 utilities
"""

# ---- Config helpers ----
from .config import (
    get_env,
    env_str,
    env_int,
    env_bool,
)

# ---- HTTP helpers ----
from .http_utils import (
    ok,
    created,
    bad_request,
    unauthorized,
    forbidden,
    not_found,
    server_error,
    parse_json_body,
    query_param,
)

# ---- Database helpers ----
from .db_utils import (
    get_connection,
    fetch_one,
    fetch_all,
    execute,
    executemany,
    get_plant_by_general_id,
    search_plants_by_name,
)

# ---- S3 helpers ----
from .s3_utils import (
    get_object_bytes,
    put_object_bytes,
    get_json,
    put_json,
    generate_presigned_get_url,
    generate_presigned_put_url,
    generate_presigned_post,
)

__all__ = [
    # config
    "get_env", "env_str", "env_int", "env_bool",
    # http
    "ok", "created", "bad_request", "unauthorized", "forbidden",
    "not_found", "server_error", "parse_json_body", "query_param",
    # db
    "get_connection", "fetch_one", "fetch_all", "execute", "executemany",
    "get_plant_by_general_id", "search_plants_by_name",
    # s3
    "get_object_bytes", "put_object_bytes", "get_json", "put_json",
    "generate_presigned_get_url", "generate_presigned_put_url", "generate_presigned_post",
]

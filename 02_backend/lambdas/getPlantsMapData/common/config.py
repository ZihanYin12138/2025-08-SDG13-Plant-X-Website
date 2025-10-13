# common/config.py
from __future__ import annotations
import os
from typing import Optional, Callable, TypeVar

T = TypeVar("T")

def _as_bool(s: str) -> bool:
    return s.strip().lower() in {"1", "true", "yes", "y", "on"}

def _convert(value: str, caster: Callable[[str], T]) -> T:
    try:
        return caster(value)
    except Exception:
        raise ValueError(f"Failed to cast env value '{value}' with {caster}")

def get_env(
    key: str,
    default: Optional[str] = None,
    cast: Optional[Callable[[str], T]] = None,
    required: bool = False,
) -> Optional[T]:
    """Read env var with optional casting and required enforcement."""
    if key in os.environ:
        raw = os.environ[key]
        return _convert(raw, cast) if cast else raw  # type: ignore
    if default is not None:
        return _convert(default, cast) if cast else default  # type: ignore
    if required:
        raise KeyError(f"Missing required environment variable: {key}")
    return None

# ---- Commonly used configs (optional helpers) ----
def env_bool(key: str, default: str = "false") -> bool:
    return get_env(key, default=default, cast=_as_bool)  # type: ignore

def env_int(key: str, default: str) -> int:
    return get_env(key, default=default, cast=int)  # type: ignore

def env_str(key: str, default: Optional[str] = None, required: bool = False) -> str:
    val = get_env(key, default=default, required=required)
    return str(val) if val is not None else ""

# lambdas/plants/run_local.py
from __future__ import annotations
import json
import sys
from pathlib import Path

# 直接调用同目录的 handler
from app import handler

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_local.py <path-to-event-json>")
        sys.exit(1)

    event_path = Path(sys.argv[1])
    event = json.loads(event_path.read_text(encoding="utf-8"))
    resp = handler(event, None)

    # 漂亮地打印输出
    print(json.dumps(resp, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

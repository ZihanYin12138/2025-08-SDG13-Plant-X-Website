from __future__ import annotations
import os, json
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import calendar
from common import fetch_one, fetch_all

# ===== Configuration =====
GARDENING_CLUBS_TABLE = os.environ.get("GARDENING_CLUBS_TABLE", "Table17_AustralianGardenClubTable")
DEFAULT_STATE = os.environ.get("DEFAULT_STATE", "ALL")
DEFAULT_DATE = os.environ.get("DEFAULT_DATE")  # Format: "YYYY-MM-DD"

# ===== Constants =====
WEEK_ORDINAL = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}
DAY_NAMES = {
    1: "Monday", 2: "Tuesday", 3: "Wednesday",
    4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"
}

# ===== Response Headers =====
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

# ===== Request Processing =====
def _extract_req(event: Dict[str, Any]) -> tuple[str, str, Dict[str, str]]:
    """Extract request method, path and query parameters"""
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

# ===== Date Processing =====
def _iso_weekday(dt: datetime) -> int:
    return dt.isoweekday()  # 1=Mon .. 7=Sun

def _week_of_month(dt: datetime) -> int:
    first = dt.replace(day=1)
    offset = first.weekday()  # Mon=0..Sun=6
    index = (offset + dt.day - 1) // 7 + 1
    return min(index, 4)

def date_from_filter(val) -> datetime:
    if val is None:
        return datetime.now()
    if isinstance(val, (datetime, date)):
        return datetime.combine(val, datetime.min.time()) if isinstance(val, date) else val
    return datetime.strptime(str(val), "%Y-%m-%d")

# ===== Time Formatting =====
def _fmt_time_12h(hhmm) -> str:
    if hhmm is None or str(hhmm).strip().lower() in ("", "nan"):
        return ""
    s = str(hhmm).strip()
    parts = s.split(":")
    h = int(parts[0])
    m = parts[1] if len(parts) > 1 else "00"
    ampm = "pm" if h >= 12 else "am"
    h12 = ((h + 11) % 12) + 1
    return f"{h12}:{str(m).zfill(2)} {ampm}"

def format_meeting_phrase(day, week, time_val) -> str:
    if day is None or not day:
        return "Not Applicable"
    day_name = DAY_NAMES.get(int(day), "")
    time_str = _fmt_time_12h(time_val)
    if week is None or not week:
        return f"Every {day_name}{(' ' + time_str) if time_str else ''}"
    return f"{WEEK_ORDINAL.get(int(week), str(int(week))+'th')} {day_name}{(' ' + time_str) if time_str else ''}"

# ===== Database Operations =====
def load_clubs(state_filter: str = "ALL", date_filter: Optional[str] = None) -> Dict[str, Any]:
    """Load gardening club data from database"""
    target_dt = date_from_filter(date_filter)
    weekday = _iso_weekday(target_dt)
    wom = _week_of_month(target_dt)

    # Use correct table field names
    base_query = f"""
        SELECT 
            Club as club_name, 
            Link as link,
            Contact as contact, 
            State as state,
            Location as location,
            Meeting_day as meeting_day, 
            Meeting_week as meeting_week, 
            Meeting_hour as meeting_hour
        FROM {GARDENING_CLUBS_TABLE}
    """

    # State filtering
    state_condition = ""
    if state_filter and state_filter.upper() != "ALL":
        state_condition = f"WHERE State = '{state_filter.upper()}'"

    # Get all clubs
    all_clubs = fetch_all(f"{base_query} {state_condition}")

    # Get today's meeting clubs
    today_query = f"""
        {base_query}
        WHERE Meeting_day = %s
        AND (Meeting_week IS NULL OR Meeting_week = %s)
        {('AND State = %s' if state_filter.upper() != 'ALL' else '')}
        ORDER BY Meeting_hour
    """
    today_params = [weekday, wom]
    if state_filter.upper() != "ALL":
        today_params.append(state_filter.upper())
    
    today_clubs = fetch_all(today_query, tuple(today_params))

    # Format results
    today_result = []
    for club in today_clubs:
        today_result.append({
            "Name": club["club_name"],
            "Link": club["link"],
            "Contact": club["contact"],
            "State": club["state"],
            "Location": club.get("location", ""),  # New location field
            "Time": _fmt_time_12h(club["meeting_hour"])
        })

    # Prepare card data
    cards_result = []
    for club in all_clubs:
        next_dt = next_occurrence(
            club["meeting_day"],
            club["meeting_week"],
            target_dt
        )
        cards_result.append({
            "Name": club["club_name"],
            "Link": club["link"],
            "Contact": club["contact"],
            "Location": club.get("location", ""),  # New location field
            "Meetings": format_meeting_phrase(
                club["meeting_day"],
                club["meeting_week"],
                club["meeting_hour"]
            ),
            "Next_meeting": fmt_date_pretty(next_dt)
        })

    return {
        "today_clubs": today_result,
        "all_clubs": cards_result
    }

# ===== Next Meeting Calculation =====
def _days_in_month(y: int, m: int) -> int:
    return calendar.monthrange(y, m)[1]

def _nth_weekday_of_month(y: int, m: int, iso_wd: int, n: int) -> datetime:
    first = datetime(y, m, 1)
    first_iso = first.isoweekday()
    delta = (iso_wd - first_iso) % 7
    day = 1 + delta + 7 * (n - 1)
    day = min(day, _days_in_month(y, m))
    return datetime(y, m, day)

def next_occurrence(meeting_day, meeting_week, ref_dt: datetime) -> datetime | None:
    if meeting_day is None or not int(meeting_day):
        return None
    wd = int(meeting_day)

    # Weekly meetings
    if meeting_week is None or not meeting_week:
        delta = (wd - ref_dt.isoweekday()) % 7
        if delta == 0:
            delta = 7
        return ref_dt + timedelta(days=delta)

    # Monthly Nth week meetings
    n = int(meeting_week)
    y, m = ref_dt.year, ref_dt.month
    cand = _nth_weekday_of_month(y, m, wd, n)
    if cand.date() <= ref_dt.date():
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1
        cand = _nth_weekday_of_month(y, m, wd, n)
    return cand

def fmt_date_pretty(dt) -> str:
    """Format date display"""
    if dt is None:
        return "Not Applicable"
    if isinstance(dt, datetime):
        return dt.strftime("%-d %B %Y")  # Linux/macOS
    return str(dt)

# ===== Lambda Handler =====
def handler(event, context):
    method, path, qs = _extract_req(event)

    if method == "OPTIONS":
        return _resp(200, {"ok": True})

    try:
        if method != "GET" or not str(path).startswith("/gardening"):
            return _resp(400, {"message": f"Unsupported route: {method} {path}"})

        qs = qs or {}
        state_filter = qs.get("state", DEFAULT_STATE).upper()
        date_filter = qs.get("date", DEFAULT_DATE)

        data = load_clubs(state_filter, date_filter)
        return _resp(200, data)

    except Exception as e:
        return _resp(500, {"message": f"internal error: {str(e)}"})
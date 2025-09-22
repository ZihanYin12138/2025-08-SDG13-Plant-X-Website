import os
import json
import pymysql

# Read environment variables (compatible with both DB_PASS / DB_PASSWORD naming)
DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ.get("DB_PASSWORD") or os.environ.get("DB_PASS")
DB_NAME = os.environ["DB_NAME"]
DB_PORT = int(os.environ.get("DB_PORT", "3306"))

# Connection placed globally for reuse
conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT,
    connect_timeout=10,
    autocommit=True,
    cursorclass=pymysql.cursors.DictCursor,  # Get dict directly, convenient for JSON conversion
)

def _maybe_parse_json(val):
    if isinstance(val, str):
        s = val.strip()
        if s.startswith("{") or s.startswith("["):
            try:
                return json.loads(s)
            except Exception:
                pass
    return val

def handler(event, context):
    # Allow passing values from event; if not passed, query general_plant_id = 1
    gid = 1
    try:
        if isinstance(event, dict):
            if "general_plant_id" in event:
                gid = int(event["general_plant_id"])
            elif event.get("queryStringParameters", {}).get("general_plant_id"):
                gid = int(event["queryStringParameters"]["general_plant_id"])
    except Exception:
        pass  # Use default 1 for invalid input

    try:
        conn.ping(reconnect=True)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM Table01_PlantMainTable WHERE general_plant_id = %s",
                (gid,),           # Parameterized to prevent SQL injection
            )
            rows = cur.fetchall()

        # If sun_expose is a JSON field, convert to Python object (optional)
        for r in rows:
            if "sun_expose" in r:
                r["sun_expose"] = _maybe_parse_json(r["sun_expose"])

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps(rows, ensure_ascii=False),
        }
    except pymysql.MySQLError as e:
        return {"statusCode": 500, "body": f"MySQL error: {e.args}"}
    except Exception as e:
        return {"statusCode": 500, "body": f"Other error: {str(e)}"}




# Return content

# Status: Succeeded
# Test Event Name: test1

# Response:
# {
#   "statusCode": 200,
#   "headers": {
#     "Content-Type": "application/json; charset=utf-8"
#   },
#   "body": "[{\"plant_id\": 1, \"general_plant_id\": 1, \"threatened_plant_id\": 0, \"common_name\": \"European Silver Fir\", \"scientific_name\": \"Abies alba\", \"other_name\": \"Common Silver Fir\", \"if_threatened\": \"False\", \"if_edible\": \"False\", \"if_indoors\": \"False\", \"if_medicinal\": \"True\", \"if_poisonous\": \"False\", \"if_fruits\": \"False\", \"if_flowers\": \"False\", \"sun_expose\": [\"full sun\"], \"watering\": \"Frequent\", \"plant_cycle\": \"Every year\", \"growth_rate\": \"High\"}]"
# }

# Function Logs:
# START RequestId: 3a4ca2eb-d8c9-4702-bce5-f3abdfb3e618 Version: $LATEST
# END RequestId: 3a4ca2eb-d8c9-4702-bce5-f3abdfb3e618
# REPORT RequestId: 3a4ca2eb-d8c9-4702-bce5-f3abdfb3e618	Duration: 29.70 ms	Billed Duration: 1465 ms	Memory Size: 128 MB	Max Memory Used: 46 MB	Init Duration: 1434.93 ms

# Request ID: 3a4ca2eb-d8c9-4702-bce5-f3abdfb3e618

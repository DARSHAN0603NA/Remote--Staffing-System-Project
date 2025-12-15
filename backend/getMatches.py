# getMatches/lambda_function.py
import os
import json
import traceback
import logging
from typing import Any, Dict

import boto3
import snowflake.connector

# config
SSM_PREFIX = os.environ.get("SSM_PREFIX", "/remote-staffing/snowflake")
REGION = os.environ.get("AWS_REGION", "eu-north-1")
CORS_ORIGIN = os.environ.get("CORS_ORIGIN", "*")

# clients
ssm = boto3.client("ssm", region_name=REGION)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# simple param cache
_PARAM_CACHE: Dict[str, str] = {}

# ---------- helpers ----------
def build_response(status: int, body_obj: Any) -> Dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": CORS_ORIGIN,
            "Access-Control-Allow-Headers": "Content-Type,x-api-key",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body": json.dumps(body_obj)
    }

def get_param(name: str) -> str:
    if name in _PARAM_CACHE:
        return _PARAM_CACHE[name]
    key = f"{SSM_PREFIX}/{name}"
    resp = ssm.get_parameter(Name=key, WithDecryption=True)
    val = resp["Parameter"]["Value"].strip()
    _PARAM_CACHE[name] = val
    return val

def get_sf_conn():
    return snowflake.connector.connect(
        user=get_param("user"),
        password=get_param("password"),
        account=get_param("account"),
        role=get_param("role"),
        warehouse=get_param("warehouse"),
        database=get_param("database"),
        schema=get_param("schema"),
        client_session_keep_alive=False
    )

def extract_payload(event: Dict) -> Dict:
    # GET query params
    qs = event.get("queryStringParameters") or {}
    if qs:
        return {
            "job_id": qs.get("job_id"),
            "top_n": qs.get("top_n")
        }

    # POST body
    body = event.get("body")
    if body:
        try:
            return json.loads(body)
        except Exception:
            pass

    return {}

# ---------- handler ----------
def lambda_handler(event, context):
    conn = None
    cur = None

    try:
        logger.info("INCOMING EVENT")

        if event.get("httpMethod") == "OPTIONS":
            return build_response(200, {"message": "OK"})

        payload = extract_payload(event)
        job_id = payload.get("job_id")

        if not job_id:
            return build_response(400, {"error": "Missing job_id"})

        try:
            top_n = int(payload.get("top_n", 10))
        except Exception:
            top_n = 10

        conn = get_sf_conn()
        cur = conn.cursor()

        db = get_param("database")
        schema = get_param("schema")

        # 1️⃣ Fetch top candidates for the job
        cur.execute(
            f"""
            SELECT CANDIDATE_ID, SCORE
            FROM {db}.{schema}.MATCH_SCORES
            WHERE JOB_ID = %s
            ORDER BY SCORE DESC
            LIMIT %s
            """,
            (job_id, top_n)
        )

        rows = cur.fetchall()
        if not rows:
            return build_response(200, {"job_id": job_id, "matches": []})

        candidate_ids = [r[0] for r in rows]

        # 2️⃣ Fetch candidate details (FIXED QUERY)
        placeholders = ",".join(["%s"] * len(candidate_ids))
        cur.execute(
            f"""
            SELECT
                CANDIDATE_ID,
                FULL_NAME,
                EMAIL,
                RESUME_TEXT
            FROM {db}.{schema}.CANDIDATE_DATA_CLEANED
            WHERE CANDIDATE_ID IN ({placeholders})
            """,
            tuple(candidate_ids)
        )

        cand_rows = cur.fetchall()
        cand_map = {
            r[0]: {
                "candidate_id": r[0],
                "full_name": r[1],
                "email": r[2],
                "resume_text": r[3]
            }
            for r in cand_rows
        }

        # 3️⃣ Merge score + details
        matches = []
        for cid, score in rows:
            info = cand_map.get(cid, {"candidate_id": cid})
            info["score"] = float(score)
            matches.append(info)

        return build_response(200, {
            "job_id": job_id,
            "matches": matches
        })

    except Exception as e:
        traceback.print_exc()
        logger.exception("Unhandled exception in getMatches")
        return build_response(500, {"error": str(e)})

    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except Exception:
            pass

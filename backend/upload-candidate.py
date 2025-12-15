import os
import json
import uuid
import logging
import boto3
import snowflake.connector
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
ssm = boto3.client("ssm")
events = boto3.client("events")

# ENV
SSM_PREFIX = os.environ.get("SSM_PREFIX", "/remote-staffing/snowflake")
EVENT_BUS = os.environ.get("EVENT_BUS", "default")
CORS_ORIGIN = os.environ.get("CORS_ORIGIN", "*")

# ---------------- helpers ----------------

def build_response(status: int, body: Any) -> Dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": CORS_ORIGIN,
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(body)
    }

def get_param(name: str) -> str:
    return ssm.get_parameter(
        Name=f"{SSM_PREFIX}/{name}",
        WithDecryption=True
    )["Parameter"]["Value"].strip()

def get_sf_conn():
    return snowflake.connector.connect(
        user=get_param("user"),
        password=get_param("password"),
        account=get_param("account"),
        role=get_param("role"),
        warehouse=get_param("warehouse"),
        database=get_param("database"),
        schema=get_param("schema")
    )

def parse_body(event: Dict) -> Dict:
    body = event.get("body", {})
    if isinstance(body, str):
        return json.loads(body)
    return body

# ---------------- handler ----------------

def lambda_handler(event, context):
    logger.info("Upload-candidate invoked")

    if event.get("httpMethod") == "OPTIONS":
        return build_response(200, {"ok": True})

    try:
        payload = parse_body(event)

        name = payload.get("name")
        email = payload.get("email")
        resume_text = payload.get("resume_text")

        if not (name and email and resume_text):
            return build_response(400, {"error": "name, email, resume_text required"})

        candidate_id = str(uuid.uuid4())

        # Insert into Snowflake
        conn = get_sf_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO JOB_PORTAL_DB.CLEAN.CANDIDATE_DATA_CLEANED
            (CANDIDATE_ID, FULL_NAME, EMAIL, RESUME_TEXT)
            VALUES (%s, %s, %s, %s)
        """, (candidate_id, name, email, resume_text))

        conn.commit()
        cur.close()
        conn.close()

        # Emit EventBridge event
        events.put_events(Entries=[{
            "Source": "remote-staffing.upload",
            "DetailType": "CandidateUploaded",
            "EventBusName": EVENT_BUS,
            "Detail": json.dumps({
                "candidate_id": candidate_id
            })
        }])

        return build_response(200, {
            "message": "Candidate uploaded",
            "candidate_id": candidate_id
        })

    except Exception as e:
        logger.exception("Upload-candidate failed")
        return build_response(500, {"error": str(e)})

import json
import boto3
from datetime import datetime
import os

REGION = "eu-north-1"
LABELS_TABLE = os.environ.get("LABELS_TABLE", "MATCH_LABELS")

ACTION_TO_LABEL = {
    "click": 1,
    "shortlist": 2,
    "apply": 3
}

dynamodb = boto3.resource("dynamodb", region_name=REGION)
labels_table = dynamodb.Table(LABELS_TABLE)

def extract_payload(event):
    # Lambda proxy integration
    if "body" in event and event["body"]:
        body = event["body"]
        if isinstance(body, str):
            return json.loads(body)
        if isinstance(body, dict):
            return body

    # Non-proxy integration (mapping / test invoke)
    return event

def lambda_handler(event, context):
    payload = extract_payload(event)

    job_id = payload.get("job_id")
    candidate_id = payload.get("candidate_id")
    action = payload.get("action")

    if not job_id or not candidate_id or action not in ACTION_TO_LABEL:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "job_id, candidate_id, and valid action required"
            })
        }

    match_id = f"{job_id}#{candidate_id}"

    labels_table.put_item(
        Item={
            "match_id": match_id,
            "label": ACTION_TO_LABEL[action],
            "event_type": action,
            "event_time": datetime.utcnow().isoformat(),
            "source": "web"
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"status": "interaction recorded"})
    }

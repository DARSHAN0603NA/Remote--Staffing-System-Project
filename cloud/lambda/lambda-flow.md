
# Lambda Execution Flow

This document explains how Lambda functions interact with other AWS services.

---

## Request Flow

1. User sends request from frontend
2. Request reaches API Gateway
3. API Gateway triggers appropriate Lambda function
4. Lambda executes backend logic
5. Data is retrieved from S3 or processed
6. Response is returned to frontend

---

## Logging & Monitoring

- All Lambda executions generate logs
- Logs are sent automatically to CloudWatch
- Metrics such as invocation count and errors are tracked

---

## Advantage

This flow ensures fast response times, scalability, and easy debugging.

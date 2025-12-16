# AWS Lambda Functions – Remote Staffing System

This document describes the AWS Lambda functions implemented for the Remote Staffing System. Lambda is used as the core compute service to execute backend logic in a serverless, scalable manner.

---

## Lambda Functions Used

### 1. remote-staffing-matcher
- Runtime: Python 3.12
- Purpose:
  - Matches job requirements with candidate profiles
  - Executes business logic for AI-based matching
- Trigger:
  - Invoked via API Gateway

### 2. list-matches
- Runtime: Python 3.12
- Purpose:
  - Retrieves previously matched candidates
  - Returns structured data to frontend
- Trigger:
  - API Gateway HTTP request

### 3. remoteStaffingBackend
- Runtime: Python 3.10
- Purpose:
  - Core backend operations
  - Handles data processing and API responses
- Trigger:
  - API Gateway

---

## Why Lambda Was Used

- No server management required
- Automatic scaling
- Cost-effective (pay per execution)
- Native integration with API Gateway, IAM, and CloudWatch

---

## Outcome

AWS Lambda enables the backend to scale automatically while remaining secure and highly available, making it ideal for the Remote Staffing System.
# Lambda Functions

This file lists the AWS Lambda functions used for lightweight event-driven tasks in the Remote Job Portal. Typical functions include small ETL steps, S3 event processors (e.g., resume parsing), webhook receivers, and scheduled jobs for maintenance or data sync.

Use this file to document each function's purpose, trigger, runtime, memory/timeout settings, and environment variables. Keep implementations small, idempotent, and well-tested; use Layers for shared dependencies.

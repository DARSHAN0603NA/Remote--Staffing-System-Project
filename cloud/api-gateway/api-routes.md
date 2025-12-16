# API Routes – Remote Staffing API

This document lists the backend routes configured in Amazon API Gateway and the Lambda functions they invoke.

---

## Configured API Routes

### 1. /matcher
- Method: POST
- Lambda Function: remote-staffing-matcher
- Description:
  - Accepts job and candidate inputs
  - Performs matching logic
  - Returns match results

---

### 2. /list-matches
- Method: GET
- Lambda Function: list-matches
- Description:
  - Fetches previously matched candidates
  - Returns structured response to frontend

---

### 3. /backend
- Method: POST / GET
- Lambda Function: remoteStaffingBackend
- Description:
  - Handles core backend operations
  - Manages application data flow

---

## Routing Flow

Frontend → API Gateway → Lambda → Response → Frontend

---

## Benefits

- Clear separation of endpoints
- Easy scalability
- Centralized API management
# API Routes

This file lists the main API routes and their purpose. The descriptions are concise and include expected HTTP method, typical parameters, and who should call them.

1. `POST /matcher`
- Purpose: request candidate-job matching for a specific job posting.
- Payload: `{ "job_id": "<id>", "candidate_ids": ["<id>"] }`
- Auth: bearer token required; application or admin role.
- Response: match results and scores.

2. `GET /matches`
- Purpose: list matches for a job or candidate.
- Query: `?job_id=<id>&candidate_id=<id>&limit=50`
- Auth: bearer token; limits enforced by scope.
- Response: paginated list of match records.

3. `POST /upload-cv`
- Purpose: upload candidate CVs (multipart/form-data) to S3 and trigger parsing.
- Payload: file upload + metadata (candidate id)
- Auth: bearer token; authenticated users and ingestion workers.
- Response: upload status and parsing job id.

4. `GET /jobs`
- Purpose: list or search job postings.
- Query: full-text `q=`, filters for location, skills, date range.
- Auth: public read for listings, authenticated for private views.

5. `POST /auth/login` and `POST /auth/refresh`
- Purpose: obtain initial tokens and refresh them. Returns JWT or OAuth2 tokens depending on implementation.

Implementation notes

- Use pagination and limit parameters for list endpoints to avoid large responses and provide stable performance.
- Validate all inputs server-side and sanitize file uploads before processing.
- Set sensible throttling on routes (API Gateway usage plans or WAF rate limits) to avoid abuse.

See `api-security.md` for authentication, authorization, and protection details.

# Amazon API Gateway – Remote Staffing System

Amazon API Gateway is used as the **central entry point** for all backend API requests in the Remote Staffing System. It securely receives HTTP requests from the frontend and routes them to appropriate AWS Lambda functions.

---

## API Created

- **API Name:** remote-staffing-api
- **API Type:** HTTP API
- **Region:** Europe (Stockholm)
- **Endpoint Type:** Regional

The API is designed to handle all backend interactions such as job matching, listing candidates, and backend data processing.

---

## Purpose of Using API Gateway

API Gateway was chosen to:
- Expose backend services securely over HTTPS
- Route requests to AWS Lambda functions
- Handle authentication and authorization
- Support scalability and traffic management

It acts as a managed layer between the frontend and backend compute services.

---

## Integration with Other Services

- Frontend communicates with API Gateway via HTTPS
- API Gateway invokes Lambda functions
- Authentication is enforced before request processing
- Logs and metrics are sent to CloudWatch

---

## Outcome

Using API Gateway provides a **secure, scalable, and managed API layer**, reducing backend complexity and improving overall system reliability.
# Remote Staffing API — Overview

The Remote Staffing API is the backend HTTP interface that powers the web dashboard, integrations, and automated match workflows. It is designed to be lightweight, secure, and observable: endpoints are organized around resources (jobs, candidates, matches, analytics), authenticated using short-lived tokens, and instrumented with structured logs and metrics for operational visibility.

Client-friendly summary

The API lets the application create and search job postings, upload candidate resumes, request automated candidate-to-job matching, and fetch reporting data for dashboards. For non-technical stakeholders, the API is the contract between the front-end and back-end: every button or page in the UI calls one or more API endpoints. It is built so that changes in the UI require minimal changes in the backend and vice versa.

Technical design highlights

- **Stateless services:** each request is self-contained and authenticated; this simplifies scaling and failure recovery.
- **Resource-oriented routes:** endpoints map to nouns (e.g., `/jobs`, `/candidates`, `/matches`) and use standard HTTP verbs.
- **Auth & authorization:** the API expects a bearer token (JWT or short-lived OAuth token) and enforces role-based access for admin operations.
- **Observability:** every request is logged with a correlation ID; critical paths emit metrics to CloudWatch for dashboards and alarms.

Deployment and hosting notes

The API is intended to be deployed behind AWS API Gateway (regional or private), backed by ECS/Fargate services or Lambda functions for specific functions. Use API Gateway for request throttling, caching, and to centralize TLS termination (ACM). Attach a WAF policy to protect against common web attacks and enable detailed access logging for audit purposes.

Use this file as the high-level explanation; see `api-routes.md` for specific endpoints and `api-security.md` for the security model.

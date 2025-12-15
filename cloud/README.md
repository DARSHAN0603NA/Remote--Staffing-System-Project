# Remote Job Portal — Cloud Folder Overview

This `cloud/` folder contains the infrastructure documentation, configuration snippets, and integration notes needed to design, deploy, operate, and govern the Remote Job Portal on AWS. The contents are written for two audiences: non-technical stakeholders who need a clear explanation of what the cloud solution delivers and technical teams who will implement, review, or extend the platform. Each section below explains the purpose of the files and gives practical guidance on how to use the artifacts found in the subfolders.

## What this folder contains

The folder is organized into focused subfolders (architecture, iam, ec2-ecs, s3, monitoring, cicd, security, snowflake-integration). Each subfolder contains short, client-friendly explanations, plus executable or copy-paste-ready snippets (JSON, YAML, Mermaid diagrams) that engineers can use as a starting point. The goal is to provide both context and concrete pieces you can reuse in your AWS account: task definitions for ECS, sample IAM policies, S3 lifecycle examples, CloudWatch dashboard guidance, a basic GitHub Actions workflow, and Snowflake integration notes.

This README explains the purpose of each area and why it matters from a business and operational perspective.

## Architecture & Diagrams

The `architecture/` subfolder includes a GitHub-renderable Mermaid diagram and a Draw.io file. The diagram provides a single-page visual of how users, load balancing (CloudFront/ALB), compute (ECS/EC2), storage (S3), secrets (Secrets Manager), monitoring (CloudWatch) and analytics (Snowflake) interact. For non-technical readers this communicates the high-level flow (user → web edge → backend → storage/analytics). For engineers, the Draw.io artifact contains the editable diagram to adapt for network segmentation, VPC subnets, and deployment zones.

Diagrams matter because they make trade-offs explicit (where we run containers vs. VMs, where data is staged, and how monitoring/alerting are connected). They also make reviews with security and compliance teams faster and more productive.

## Security, IAM & Secrets

Security is documented in `iam/` and `security/`. Expect readable role descriptions, starter IAM policy JSON, and best-practice notes for least-privilege. The `secrets-manager.md` explains how to keep credentials out of code, and `encryption-strategy.md` covers TLS/KMS choices. These docs are intentionally practical: they describe what to implement, why it matters (risk reduction, auditability), and how to scope policies so your operations team can apply them with minimal risk.

From a client perspective: these files show we designed the system with enterprise-grade security controls in mind — no embedded secrets, scoped roles per environment, and audit trails (CloudTrail) for all privileged activity.

## Compute and Deployment (EC2 / ECS / CI-CD)

The `ec2-ecs/` and `cicd/` folders contain the deployment artifacts and brief runbooks. You will find an example ECS task definition (Fargate mode), a compact deployment checklist, and a GitHub Actions template to wire into a CI pipeline. These files are intentionally minimal so they can be dropped into a pipeline and expanded to match your naming conventions, registries (ECR), and environment variables.

Why this matters: automation reduces human error and speeds releases. The provided snippets let DevOps teams stand up a repeatable build→test→deploy flow quickly while maintaining control via IAM roles and secure secret injection.

## Storage & Data Lifecycle (S3)

The `s3/` folder explains bucket organization (raw, clean, artifacts), includes a sample bucket policy JSON, and lifecycle examples for cost control. It shows recommended retention policies — e.g., short retention for temp files and longer archival for compliance artifacts — plus encryption and access-control recommendations.

Business value: S3 rules protect data, reduce monthly costs through lifecycle transitions, and make audits straightforward by recording access and lifecycle actions.

## Monitoring & Alerts

`monitoring/` contains CloudWatch dashboard recommendations, alarm definitions, and logging strategy guidance. These documents explain which metrics to track (CPU, memory, latency, error rates), how to centralize logs, and how to route alerts to on-call and product channels. We recommend structured JSON logs, correlation IDs, and retention policies that balance cost and compliance.

Monitoring ensures visibility into system health and enables rapid incident response — a critical business requirement for production services.

## Analytics Integration (Snowflake)

The `snowflake-integration/` folder describes secure staging patterns (S3 → Snowpipe), IAM-based external stages, and Snowpark usage for in-database transformations. This section explains why Snowflake is used for analytics and how to securely move data there without exposing credentials.

Analytics value: it enables business reporting, recruiter performance metrics, and ML workflows while keeping operational systems isolated.

## How to use these files

- Review the `architecture/` diagram with your network/security team first.
- Replace placeholder ARNs and bucket names in the JSON snippets with your account-specific values.
- Use the ECS task definition and GitHub Actions template as a starting point: integrate with your ECR registry, secrets, and environment variables.
- Apply IAM policies in a staging account and test behavior with IAM Access Analyzer and CloudTrail before promoting to production.

If you want, I can expand any of the subfolder documents into longer runbooks, generate Terraform/CloudFormation from the snippets, or produce a one-page executive summary suitable for board-level review.

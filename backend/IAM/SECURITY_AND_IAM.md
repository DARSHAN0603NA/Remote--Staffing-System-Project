# Security & IAM Design — Snowflake + AWS Lambda Backend

This project uses **AWS Lambda** as the backend compute layer with **Snowflake** as the analytical data warehouse.  
IAM policies are designed to securely manage configuration, secrets, storage, and event-driven workflows while following **least-privilege** and **production-grade security practices**.

⚠️ **Security Notice**  
All IAM policies in this repository are **sanitized templates**. Real AWS account IDs, regions, bucket names, and secret identifiers are intentionally replaced with placeholders.

---

## Architecture Overview

- **AWS Lambda** – Executes backend logic (ingestion, processing, Snowflake interaction)
- **AWS SSM Parameter Store** – Stores encrypted Snowflake configuration (account, role, warehouse)
- **AWS Secrets Manager** – Stores Snowflake credentials securely
- **Amazon S3** – Stores intermediate data and ML artifacts
- **Amazon EventBridge** – Enables event-driven processing
- **Amazon CloudWatch Logs** – Centralized logging
- **AWS KMS** – Encrypts sensitive configuration and secrets

---

## IAM Design Principles

- **Least Privilege** – Permissions scoped only to required services
- **Separation of Concerns** – Policies split by responsibility
- **Secure Secret Handling** – No credentials in code or repositories
- **Public Repo Safety** – Infrastructure identifiers are sanitized

---

## IAM Policies Used

### 1️⃣ SSM + KMS + Logs Policy  
**Purpose:** Securely retrieve Snowflake configuration

- Reads encrypted Snowflake parameters from **SSM Parameter Store**
- Decrypts parameters using **KMS** (restricted to SSM usage only)
- Writes Lambda execution logs to **CloudWatch Logs**

This ensures Snowflake connection details are never hardcoded.

---

### 2️⃣ Secrets Manager + S3 + Logs Policy  
**Purpose:** Runtime data access and storage

- Retrieves Snowflake credentials from **Secrets Manager**
- Reads/writes files and artifacts in **Amazon S3**
- Publishes logs to **CloudWatch Logs**

Secrets access is scoped using naming prefixes to avoid over-permissioning.

---

### 3️⃣ EventBridge Publish Policy  
**Purpose:** Event-driven backend workflows

- Allows Lambda to publish events (e.g., job upload, processing completion)
- Enables loose coupling between backend components

---

## Why Policies Are Modular

IAM policies are **not merged** into a single policy.

**Benefits:**
- Easier auditing and debugging
- Clear security boundaries
- Enterprise-style IAM structure
- Safer future permission updates

This mirrors real-world cloud security design.

---

## How Snowflake Credentials Are Secured

- Credentials are stored in **AWS Secrets Manager**
- Connection configuration is stored in **SSM Parameter Store**
- All values are encrypted using **AWS KMS**
- Lambda retrieves values at runtime only
- No secrets are committed to version control

---

## Interview-Ready Summary

> “The backend uses AWS Lambda with Snowflake as the data warehouse.  
> IAM policies follow least privilege and are split by responsibility.  
> Snowflake credentials are securely stored in Secrets Manager, configuration in SSM, and decrypted via KMS at runtime.  
> Public repositories contain sanitized IAM templates to prevent infrastructure exposure.”

---

## Final Note

This IAM setup reflects **production-grade Snowflake + AWS Lambda security practices**, balancing flexibility, security, and maintainability.

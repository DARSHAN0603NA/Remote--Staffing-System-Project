# IAM Roles and Access Management – Remote Job Portal

This document explains how **AWS Identity and Access Management (IAM)** roles were designed and implemented for the Remote Job Portal. IAM plays a critical role in securing the cloud infrastructure by controlling who can access AWS resources and what actions they are allowed to perform. In this project, IAM was configured following the **principle of least privilege**, which is a core security best practice.

---

## Purpose of IAM in This Project

The Remote Job Portal consists of multiple AWS services such as ECS, EC2, S3, CloudWatch, and CI/CD pipelines. Each of these services requires specific permissions to function correctly. Instead of using long-term credentials or granting full access, IAM roles were created to provide **temporary, scoped permissions** to services.

The main goals of using IAM were:
- Prevent unauthorized access
- Avoid hard-coded credentials
- Enable secure service-to-service communication
- Support auditing and compliance

---

## IAM Roles Created

### 1. Backend Service Role

This role is attached to the ECS tasks running the backend application.

**Permissions granted:**
- Read and write access to specific S3 buckets
- Permission to write logs to CloudWatch
- Read access to secrets stored in AWS Secrets Manager

**How it is created:**
1. An IAM role is created in the AWS console.
2. ECS is selected as the trusted service.
3. Custom policies are attached with only required permissions.
4. The role is referenced in the ECS task definition.

**Access Point:**
- The role is automatically assumed by ECS tasks at runtime.
- No user credentials are required.

---

### 2. CI/CD Pipeline Role

This role is used by GitHub Actions to deploy the application.

**Permissions granted:**
- Update ECS services
- Register new task definitions
- Access required AWS resources for deployment

**How it is created:**
1. An IAM role is created for external access.
2. Trust policy allows GitHub Actions to assume the role.
3. Deployment-specific permissions are attached.

**Access Point:**
- Accessed only during deployment through secure authentication.

---

## Advantages of Using IAM Roles

- Eliminates the need for storing AWS keys in code
- Reduces security risks through scoped permissions
- Enables secure automation
- Supports audit logging via AWS CloudTrail

---

## Conclusion

IAM roles form the foundation of the security model for the Remote Job Portal. By separating permissions based on responsibility and attaching roles directly to services, the system achieves a high level of security, flexibility, and maintainability. This approach reflects real-world cloud security practices and is suitable for production environments.


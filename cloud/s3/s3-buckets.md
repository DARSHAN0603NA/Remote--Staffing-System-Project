# Amazon S3 Buckets – Remote Job Portal

This document explains how **Amazon Simple Storage Service (S3)** is used in the Remote Job Portal for secure, scalable, and cost-effective storage. S3 plays an important supporting role in the architecture by storing application assets, logs, configuration files, and data required for analytics workflows.

---

## Purpose of Using Amazon S3

The Remote Job Portal generates and consumes different types of data that do not require a traditional database. These include static files, log data, configuration artifacts, and intermediate data for analytics. Amazon S3 was selected to handle these storage requirements due to its durability, scalability, and seamless integration with other AWS services.

The key objectives of using S3 were:
- Secure storage of non-relational data
- High availability and durability
- Easy integration with ECS, CloudWatch, and Snowflake
- Cost-efficient data management

---

## Types of Buckets Used

Multiple S3 buckets were created, each with a clear and specific purpose:

- **Assets Bucket** – Stores static assets such as documents or exported reports.
- **Logs Bucket** – Stores application and access logs for monitoring and auditing.
- **Configuration Bucket** – Stores configuration files required by backend services.
- **Analytics Staging Bucket** – Used to stage data before it is transferred to Snowflake.

Separating data by purpose improves security, manageability, and access control.

---

## How the Buckets Were Created

1. S3 buckets were created using the AWS Management Console.
2. Region selection was aligned with compute services to reduce latency.
3. Public access was blocked by default.
4. Server-side encryption was enabled to protect stored data.
5. Versioning was enabled for critical buckets to allow recovery from accidental deletions.
6. Bucket policies were applied to restrict access using IAM roles.

---

## Access Control and Security

- Buckets are accessed only through **IAM roles**, not user credentials.
- Backend ECS services have limited permissions to specific buckets.
- Public access is disabled unless explicitly required.
- All access actions are logged for auditing purposes.

The access point for S3 is private and controlled programmatically through AWS SDKs used by backend services.

---

## Advantages of Using Amazon S3

- Extremely high durability and availability
- Scales automatically without capacity planning
- Strong security features including encryption and access control
- Supports lifecycle policies for cost optimization
- Easy integration with analytics platforms

---

## Limitations and Considerations

- Improper policies can cause security issues
- Costs can increase without lifecycle rules
- Not suitable for transactional workloads

---

## Conclusion

Amazon S3 provides a **reliable and secure storage backbone** for the Remote Job Portal. Its integration with compute, monitoring, and analytics services allows the system to store and manage data efficiently while maintaining strong security controls. The S3 design reflects best practices suitable for both academic evaluation and real-world deployment.
# Storage Overview

AWS S3 stores system files and logs.

## What is Stored
- User uploads
- Application logs
- Reports

## Why S3
- Secure
- Scalable
- Cost efficient


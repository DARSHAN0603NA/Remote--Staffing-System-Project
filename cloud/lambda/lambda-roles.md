# Lambda IAM Roles – Access Control

Each Lambda function uses a dedicated IAM execution role to follow the principle of least privilege.

---

## Roles Used

### remote-staffing-lambda-role
Permissions:
- Read/write access to required S3 buckets
- Write logs to CloudWatch
- Access Secrets Manager (read-only)

### remoteStaffingBackend-role
Permissions:
- Invoke dependent Lambda functions
- Access analytics staging S3 bucket
- Write metrics to CloudWatch

---

## Security Benefits

- No hardcoded credentials
- Scoped permissions per function
- All access is auditable via AWS IAM

---

## Conclusion

Using IAM roles ensures secure and controlled execution of Lambda functions while protecting sensitive AWS resources.
# Lambda Roles

Document the IAM roles assigned to Lambda functions here. Roles should be narrowly scoped: give S3 read/write only to the specific buckets a function needs, grant Secrets Manager read access only for secret ARNs the function requires, and avoid using account-wide wildcards.

Include example trust policy and minimal inline policy snippets, and reference the role name convention used by your deployment pipeline.

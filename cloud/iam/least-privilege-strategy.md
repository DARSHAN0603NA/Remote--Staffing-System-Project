# Least Privilege Strategy

The principle of least privilege means granting identities (users, roles, services) only the minimum permissions they need to perform their tasks — and no more. This reduces the blast radius of accidental or malicious actions, simplifies audits, and makes compliance easier to demonstrate.

What we recommend for the Remote Staffing System:

- Use short-lived credentials via IAM roles (ECS task roles, EC2 instance roles, and CI/CD deployment roles) instead of static access keys. Roles provide temporary credentials and remove the need to embed secrets in code.
- Create narrowly-scoped policies targeting specific ARNs (for example, `arn:aws:s3:::remote-staffing-raw-dev/*`) rather than using wildcards across the account. Scope by resource, action, and when useful, by condition keys (IP ranges, VPC source, tags).
- Separate duties by environment and function: different roles for `dev`, `staging`, and `prod` and different roles for `app`, `analytics`, and `deployment` flows. This avoids cross-environment contamination and makes revocation easier.

How to implement (practical steps):

1. Inventory: list the resources each service requires (S3 paths, Secrets Manager entries, KMS keys, etc.).
2. Policy-first: create minimal policies that allow only those actions on those resources. Attach policies to roles, not users.
3. Iterate: start with read-only access where possible and add write privileges only when necessary.
4. Use AWS managed features: session policies, AWS Organizations SCPs, and IAM Access Analyzer to validate and detect overly-broad permissions.

Operational best practices:

- Tag and document roles and policies so reviewers understand their purpose.
- Enable CloudTrail and set alerts for unusual IAM activity (policy changes, role assumption from unexpected sources).
- Regularly run automated checks (IAM Access Analyzer, policy simulations) and code review for IAM policy changes in PRs.

Adopting least privilege is an iterative process — start narrow, monitor failures, and widen only when justified. This ensures strong security posture while keeping developer workflows frictionless.

# SSL/TLS using AWS Certificate Manager

AWS Certificate Manager (ACM) is used to enable secure HTTPS communication.

---

## Implementation

- SSL certificate issued via ACM
- Integrated with CloudFront
- Enforces encrypted communication

---

## Security Advantage

- Protects data in transit
- Improves trust and compliance
- Eliminates manual certificate management
# SSL / ACM

Document how TLS certificates are provisioned for the project. Use AWS Certificate Manager (ACM) for public certificates in us-east-1 (recommended for CloudFront) and regional ACM for load balancers. Include steps for validation (DNS validation via Route53), certificate rotation, and mapping certificates to CloudFront distributions or ALBs.

Also note any wildcard or SAN certificate requirements and how to store certificate ARNs in the deployment pipeline.

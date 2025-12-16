# CloudFront Distribution – Frontend Delivery

Amazon CloudFront is used to deliver frontend assets globally with low latency.

---

## Configuration

- Origin: S3 (remote-staffing-frontend)
- Protocol: HTTPS
- Caching enabled
- Global edge locations

---

## Benefits

- Faster content delivery
- Reduced load on backend
- Improved user experience
# CloudFront Distribution

This file describes the recommended CloudFront distribution configuration for serving static assets and protecting the application edge. Documented values should include origin (S3 bucket or ALB), behavior (cache TTLs, compressions), security (WAF, TLS minimum versions), and signed URL/Cookie strategy if content should be restricted.

Include notes for invalidation strategy after deployments and for setting up origin failover if using multiple origins.

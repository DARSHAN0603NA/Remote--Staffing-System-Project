# Lifecycle Rules

Lifecycle rules automate the movement and expiration of objects in S3 to control storage costs and implement retention policies. For the Remote Staffing System we use lifecycle policies to ensure short-lived files (temporary processing artifacts, upload caches) expire quickly while archival data is moved to lower-cost tiers.

Key principles:

- **Cost control**: move less-frequently accessed objects to `STANDARD_IA`, `ONEZONE_IA`, or `GLACIER` after a defined period.
- **Retention & compliance**: retain required records for compliance, and expire (delete) temporary or test data automatically.
- **Predictability**: deterministic transitions reduce surprises in monthly billing and simplify retention audits.

Example rules (common patterns):

1. Temporary files: transition to `Standard-IA` after 30 days, expire after 90 days.
2. Reports and exports: transition to `Glacier` after 365 days for long-term archival.
3. Versioned buckets: keep non-current versions for 365 days then permanently delete.

Example lifecycle configuration (JSON):

```json
{
	"Rules": [
		{
			"ID": "temp-files",
			"Filter": {"Prefix": "tmp/"},
			"Status": "Enabled",
			"Transitions": [{"Days": 30, "StorageClass": "STANDARD_IA"}],
			"Expiration": {"Days": 90}
		}
	]
}
```

Implementation notes:

- Apply lifecycle rules at the bucket level and test them in a staging bucket first.
- Monitor the first few months of transitions to ensure objects are being moved as expected (use S3 Inventory reports).
- Be cautious with transition into Glacier Flexible Retrieval or Deep Archive — retrieval costs and latencies can be significant, so reserve deep archive for rarely-accessed, long-retention data.

Operationally, lifecycle rules are a low-maintenance way to enforce retention policies and reduce costs while keeping the data governance process auditable.

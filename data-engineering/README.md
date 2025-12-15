## Data Engineer – Role & Responsibilities

As the Data Engineer for the Remote Staffing System, my responsibility was to design, implement, and manage the complete data infrastructure that enables automated job data ingestion, structured storage, transformation, and analytics-ready data preparation.

I developed Python-based ETL pipelines to collect job data from multiple external APIs including JSearch, Adzuna, and Jooble. These pipelines handle pagination, data extraction, and conversion of raw API responses into structured datasets for further processing.

I designed and implemented a layered Snowflake data warehouse architecture consisting of RAW, CLEAN, and BI schemas. Raw data is first ingested into the RAW layer, followed by data cleaning, normalization, and deduplication in the CLEAN layer. The BI layer contains aggregated and optimized tables for reporting and analytics.

Automation was configured using Windows Task Scheduler to ensure regular data refresh without manual intervention. I also implemented role-based access control in Snowflake to support secure access for AI, backend, and analytics users.

The final output of this work is a scalable, secure, and production-ready data pipeline that supports AI-based job–candidate matching and real-time Power BI dashboard analytics.

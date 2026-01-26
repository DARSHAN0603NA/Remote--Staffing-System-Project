# **Remote Staffing System**

## **Project Overview**

The Remote Staffing System is an end-to-end recruitment analytics and matching platform designed to automate job data collection, enable AI-based job–candidate matching, and provide real-time recruitment insights through dashboards. The system integrates multiple job platforms, cloud-based data processing, AI components, backend services, and visualization tools into a single scalable solution.


## **System Architecture**

The system follows a modular, layered architecture consisting of data ingestion, data processing, AI analytics, backend services, cloud deployment, and visualization layers.

<img width="4123" height="2575" alt="Architecture Diag  Light" src="https://github.com/user-attachments/assets/df28d578-1928-4719-81ac-88543744b28a" />


## **Architecture Flow**

Job Platform (Adzuna)  
→ Python-based ETL Pipelines  
→ Snowflake Data Warehouse (RAW → CLEAN → BI)  
→ AI & Embedding Generation  
→ Backend APIs (Cloud Hosted)  
→ Power BI Dashboards & Frontend Interface  

This architecture ensures automation, scalability, security, and real-time analytics delivery.


 ## **Team Roles & Responsibilities**


## **Power BI Analyst & Documentation (DARSHAN N A)**
- Designed and developed three role-based Power BI dashboards (Admin, Recruiter, Candidate) for a Remote Staffing System  
- Built meaningful KPIs and business-focused visuals to track growth, performance, and platform health  
- Implemented interactive features such as slicers, cross-filtering, and drill-down for better user exploration  
- Applied data modeling and basic DAX measures to support accurate insights and analytics  
- Documented dashboard objectives, features, and usage to clearly communicate project outcomes

 ## **Data Engineer (TANISHA K S)**
- Designed and implemented the Snowflake data warehouse architecture
- Built automated ETL pipelines for multi-source job data ingestion
- Cleaned, normalized, and deduplicated job and candidate datasets
- Prepared analytics-ready tables for AI processing and dashboards
- Implemented secure role-based access and data consistency mechanisms


 ## **AI/ML Engineer (ABHISHEK H G)**
- Generated embeddings for job descriptions and candidate profiles
- Implemented similarity-based job–candidate matching logic
- Computed and stored match scores in Snowflake
- Enabled intelligent and scalable recruitment recommendations


 ## **Backend Developer (SUSHMITHA C)**
- Developed backend APIs for job upload, candidate upload, and matching services
- Integrated backend services with Snowflake and AI components
- Ensured secure and reliable data flow between system layers

 ## **Frontend Developer (SHREYA P)**
- Designed user interfaces for job and candidate interactions
- Integrated frontend with backend APIs
- Displayed recruitment insights and matching results to end users


 ## **Cloud / DevOps Engineer (MEGHANA B)**
- Deployed backend services using cloud infrastructure (AWS)
- Configured AWS Lambda functions for scalable backend execution
- Integrated API Gateway for secure API exposure
- Managed IAM roles and permissions for secure access control
- Implemented parameter management and secrets storage using AWS SSM
- Ensured monitoring, logging, and system reliability through cloud services


## **Key Features**
- Automated job data ingestion from multiple platforms
- Scalable Snowflake data warehouse with layered design
- AI-driven job–candidate matching
- Cloud-hosted backend services
- Interactive dashboards for recruitment insights
- Secure, role-based data access
- End-to-end automation and analytics pipeline


 ## **Technologies Used**
- Python
- Snowflake
- SQL
- Power BI
- REST APIs
- AI/ML (Embeddings & Similarity Matching)
- AWS (Lambda, API Gateway, IAM, SSM)
- Git & GitHub


 ## **Conclusion**
 
The Remote Staffing System demonstrates a complete, production-ready recruitment analytics solution integrating data engineering, AI processing, cloud deployment, backend services, and visualization. The project highlights how modern cloud-based architectures enable intelligent and data-driven hiring decisions.

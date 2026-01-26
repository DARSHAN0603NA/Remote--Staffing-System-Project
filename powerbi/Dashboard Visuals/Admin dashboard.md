# Admin Dashboard – Remote Staffing System

##  Project Overview
This project showcases an *Admin Dashboard built using Microsoft Power BI* to monitor platform activity, data health, and operational trends.  
The dashboard is designed to help administrators track growth, ensure data freshness, and understand high-level usage patterns.

It demonstrates:
- KPI design  
- Dashboard structuring  
- Power BI visualization best practices  
- Business-focused analytics  

---

##  Dashboard Features

The Admin Dashboard includes the following insights:

###  Growth & Activity Metrics
- *Jobs Ingested Over Time* – Tracks how many new jobs enter the system daily  
- *Candidates Onboarded Over Time* – Shows candidate growth trend  

###  Operational Metrics
- *Recruiter Approved Candidates* – Count of active/valid candidates  
- *Matches Generated* – Represents overall matching potential between candidates and jobs  

###  Platform Health Metrics
- *Latest Job Data Refresh Date*  
- *Latest Candidate Data Refresh Date*  
- *Jobs by Source* – Distribution of data sources to monitor data pipeline quality  

### Trends & Insights
- *Jobs by Title* – Hiring trends across job roles  
- *Jobs by Location* – Geographic hiring demand  
- *Demand by Requested Role* – Candidate interest by role  

---

##  Data Sources Used

Two datasets were used:

### JOBS_FACT
- JOB_ID  
- TITLE  
- COMPANY  
- LOCATION  
- SOURCE  
- CREATED_AT  
- INGESTION_DATE  

### CANDIDATES_FACT
- CANDIDATE_ID  
- FULL_NAME  
- EMAIL  
- ROLE  
- REQUESTED_ROLE  
- CREATED_AT  
- INGESTION_DATE  

---

##  Dashboard Preview


<img width="764" height="448" alt="image" src="https://github.com/user-attachments/assets/f5e361fb-d497-4106-ae11-45de09ea44ad" />

---

##  Tools & Technologies
- Microsoft Power BI  
- DAX (basic measures)  
- Data Modeling  
- CSV datasets  
- GitHub for project versioning  

---

##  How to Use This Project
1. Download the .pbix file from the repository  
2. Open it using *Power BI Desktop*  
3. Explore the dashboard visuals and interactions  
4. Review the data model and measures  

---

## 👤 Author
*Darshan N A*

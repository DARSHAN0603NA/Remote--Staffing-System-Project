# Recruiter Dashboard – Remote Staffing System

##  Project Overview
This project showcases a *Recruiter Dashboard built using Microsoft Power BI* to help recruiters monitor hiring activity, evaluate candidate-job matching, and make faster data-driven decisions.  
The dashboard focuses on improving recruiter productivity by providing clear visibility into candidate pipelines and match quality.

It demonstrates:
- KPI-driven dashboard design  
- Recruiter-focused analytics  
- Interactive filtering and exploration  
- Power BI visualization best practices  

---

##  Dashboard Features

The Recruiter Dashboard provides the following insights:

###  Recruitment Overview Metrics
- *Total Candidates* – Total candidates available for review  
- *Total Matches* – Number of candidate-job matches generated  
- *Average Match Score* – Overall quality of matches  
- *High Quality Matches %* – Percentage of strong matches  

###  Matching & Performance Insights
- *Match Score Distribution* – View of low, medium, and high match ranges  
- *Matches per Job* – Identifies jobs receiving the most matches  
- *Candidates by Role* – Distribution of candidates across roles  

###  Recruiter-Focused Analysis
- *Top Matching Candidates* – Easily identify best-fit candidates  
- *Job-wise Match Analysis* – Understand which roles attract strong candidates  

###  Interactivity
- Slicers for dynamic filtering by:
  - Role  
  - Requested Role  
  - Company  
  - Location  
- Enables quick drill-down and focused analysis  

---

##  Data Sources Used

The dashboard uses structured datasets including:

### CANDIDATES_FACT
- CANDIDATE_ID  
- FULL_NAME  
- EMAIL  
- ROLE  
- REQUESTED_ROLE  
- CREATED_AT  
- INGESTION_DATE  

### JOBS_FACT
- JOB_ID  
- TITLE  
- COMPANY  
- LOCATION  
- SOURCE  
- CREATED_AT  
- INGESTION_DATE  

### (Optional if included in your model)
### MATCHES_FACT
- MATCH_ID  
- JOB_ID  
- CANDIDATE_ID  
- MATCH_SCORE  
- CREATED_AT  
- INGESTION_DATE  

---

##  Dashboard Preview

<img width="688" height="501" alt="image" src="https://github.com/user-attachments/assets/ae9e9889-d005-43bd-9790-2c50a6ff2bb9" />


---

##  Tools & Technologies
- Microsoft Power BI  
- DAX (for KPIs and measures)  
- Data Modeling (fact tables)  
- CSV datasets  
- GitHub for project versioning  

---

##  How to Use This Project
1. Download the .pbix file from this repository  
2. Open it using *Power BI Desktop*  
3. Use slicers to filter by role, company, and location  
4. Explore KPIs and visuals to understand recruiter insights  

---

##  Author
*Darshan N A*

*Final Year BE-Artificial Intelligence and Data Science*

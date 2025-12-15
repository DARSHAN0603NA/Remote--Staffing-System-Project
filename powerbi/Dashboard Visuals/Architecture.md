
## Power BI Analytics Architecture

### Architecture Diagram


```mermaid
flowchart TD

    Snowflake_Data["Snowflake Data Warehouse (CLEAN & BI Tables)"]
    PowerBI_Desktop["Power BI Desktop"]
    Data_Modeling["Data Modeling (Relationships & Measures)"]
    Dashboard_Development["Dashboard Development (KPIs, Charts, Filters)"]
    PowerBI_Service["Power BI Service"]
    Users["Frontend / Business Users"]
    Data_Refresh["Scheduled Data Refresh (Snowflake Credentials)"]
    Insights["Recruitment Insights (Trends, Skills, Salary)"]

    Snowflake_Data --> PowerBI_Desktop
    PowerBI_Desktop --> Data_Modeling
    Data_Modeling --> Dashboard_Development
    Dashboard_Development --> PowerBI_Service
    PowerBI_Service --> Users
    PowerBI_Service --> Data_Refresh
    Users --> Insights


## Architecture Explanation


The Power BI analytics architecture is built on top of the Snowflake Data Warehouse, which stores cleaned and analytics-ready job data in the CLEAN and BI schemas. This ensures that only high-quality, standardized data is used for reporting and analysis.

Power BI Desktop connects directly to Snowflake to import the required datasets. Within Power BI Desktop, data modeling is performed by defining table relationships, calculated columns, and measures to ensure accurate aggregations and consistent reporting logic.

After data modeling, interactive dashboards are developed using KPI cards, charts, tables, and filters to visualize hiring trends, salary distribution, skill demand, and job market insights.

The completed dashboards are published to Power BI Service, which serves as the central platform for hosting, sharing, and managing reports. Power BI Service enables secure access for frontend and business users and supports scheduled data refresh using Snowflake credentials to keep dashboards up to date.

This architecture provides a scalable, secure, and interactive analytics layer that delivers real-time recruitment insights without requiring users to directly access the underlying data warehouse.

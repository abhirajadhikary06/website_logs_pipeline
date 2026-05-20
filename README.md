┌──────────────────────────────────────────────────────────────┐
│                    SOURCE LAYER (OLTP)                      │
│──────────────────────────────────────────────────────────────│
│ Neon PostgreSQL                                             │
│                                                             │
│ Tables:                                                     │
│ - website_checks_log                                        │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               │ Incremental Extraction
                               │ using checked_at
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                  INGESTION + BRONZE LAYER                   │
│──────────────────────────────────────────────────────────────│
│ dlt + Polars                                                │
│                                                             │
│ Responsibilities:                                           │
│ - Incremental ingestion                                     │
│ - Lightweight cleaning                                      │
│ - URL normalization                                         │
│ - Domain extraction                                         │
│ - Response time conversion                                  │
│ - Status categorization                                     │
│ - Error flagging                                            │
│ - Performance bucketing                                     │
│ - Timestamp feature extraction                              │
│ - Metadata enrichment                                       │
│ - Bronze standardization                                    │
│                                                             │
│ Output: Bronze-ready analytical data                        │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               │ Load Bronze Data
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    WAREHOUSE LAYER                          │
│──────────────────────────────────────────────────────────────│
│ DuckDB                                                      │
│                                                             │
│ Schemas:                                                    │
│ - bronze                                                    │
│ - silver                                                    │
│ - gold                                                      │
│ - marts                                                     │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               │ SQL Modelling
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    SILVER LAYER (dbt)                       │
│──────────────────────────────────────────────────────────────│
│ Business-ready analytical models                            │
│                                                             │
│ Responsibilities:                                           │
│ - Reusable analytics logic                                  │
│ - Joins                                                     │
│ - Intermediate models                                       │
│ - Fact table modelling                                      │
│ - Dimension table modelling                                 │
│ - Surrogate keys                                            │
│ - Data quality tests                                        │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               │ Aggregation & KPI Modelling
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    GOLD / MARTS LAYER                       │
│──────────────────────────────────────────────────────────────│
│ Department-focused analytical marts                         │
│                                                             │
│ Marts:                                                      │
│ - uptime_mart                                               │
│ - performance_mart                                          │
│ - error_analysis_mart                                       │
│ - domain_monitoring_mart                                    │
│ - latency_trends_mart                                       │
│ - executive_kpi_mart                                        │
└──────────────────────────────┬───────────────────────────────┘
                               │
             ┌─────────────────┴──────────────────┐
             │                                    │
             ▼                                    ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│     BI DASHBOARDS        │      │     VECTOR DATABASE      │
│──────────────────────────│      │──────────────────────────│
│ Lightdash                │      │ Qdrant                   │
│                          │      │                          │
│ Dashboarding from marts  │      │ Semantic Search          │
│ KPI Visualizations       │      │ RAG Retrieval            │
│ Business Analytics       │      │ Embedding Storage        │
└──────────────────────────┘      └──────────────┬───────────┘
                                                 │
                                                 ▼
                                        ┌────────────────────┐
                                        │    Streamlit       │
                                        │────────────────────│
                                        │ RAG Application UI │
                                        │ Chat Interface     │
                                        │ Semantic Querying  │
                                        └────────────────────┘
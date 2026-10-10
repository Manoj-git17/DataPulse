# DataPulse — Intelligent Data Engineering & Analytics Platform

An end-to-end data engineering and analytics solution built with Python, Pandas, PostgreSQL, FastAPI, and React.

---

## 🎯 Project Overview

**DataPulse** simulates a real-world enterprise analytics pipeline:
1. **Ingest & Validate**: Ingest raw sales and transactional data with automated schema validation.
2. **Transform & Clean**: Apply ETL processing, anomaly filtering, and metric calculation using Pandas.
3. **Model & Store**: Persist structured, normalized entities into a PostgreSQL analytical warehouse.
4. **Analyze (SQL)**: Compute KPIs, customer segments, moving averages, and cohort retention.
5. **Serve (FastAPI)**: Expose high-performance REST APIs for business metrics.
6. **Visualize (React)**: Render interactive dashboards with visual trends and filters.

---

## 🛠️ Technology Stack

- **Data Engineering**: Python, Pandas
- **Database & Modeling**: PostgreSQL, SQL
- **Backend API**: FastAPI, Uvicorn, SQLAlchemy
- **Frontend Dashboard**: React, Vite
- **Version Control**: Git, GitHub

---

## 📁 Project Structure

```text
DataPulse/
├── .env.example          # Environment variable template
├── .gitignore            # Git exclusion rules
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── data/
│   ├── raw/              # Immutable raw incoming datasets
│   └── processed/        # Cleaned, transformed data artifacts
├── db/                   # Database schemas, migrations, and SQL queries
├── etl/                  # Python ETL ingestion and transformation modules
├── backend/              # FastAPI application (Phase 7)
├── frontend/             # React dashboard (Phase 6)
└── tests/                # Automated unit and integration tests
```

---

## 🚀 Development Roadmap

- [x] **Phase 1**: Environment setup and project structure
- [x] **Phase 2**: Import and validate sales data using Python & Pandas
- [x] **Phase 3**: Clean and transform the data
- [x] **Phase 4**: Store the processed data in PostgreSQL / Relational DB
- [x] **Phase 5**: Build SQL analytics
- [x] **Phase 6**: Create a dashboard using React
- [x] **Phase 7**: Connect dashboard to FastAPI backend
- [ ] **Phase 8**: Testing, documentation, and deployment preparation
- [ ] **Phase 9**: AI assistant (advanced feature)

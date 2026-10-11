# DataPulse — Intelligent Data Engineering & Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.143-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2-61DAFB.svg)](https://react.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1-red.svg)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791.svg)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/Tests-26%20Passed-brightgreen.svg)]()
[![Budget](https://img.shields.io/badge/Budget-₹0%20(Open%20Source)-success.svg)]()

> **DataPulse** is an end-to-end, enterprise-grade data engineering, SQL analytics, and full-stack platform built with Python, Pandas, PostgreSQL/SQLite, FastAPI, and React. Built from the ground up at **₹0 cost** using pure open-source technologies.

---

## 🏗️ System Architecture

```mermaid
flowchart LR
    subgraph Ingestion & ETL
        Raw["Raw CSV Data\n(data/raw/)"] --> Ingest["Ingestion\n(etl/ingest.py)"]
        Ingest --> Validate["Validation Engine\n(etl/validate.py)"]
        Validate --> Transform["Transformation\n(etl/transform.py)"]
        Validate -.-> Quarantine["Quarantine Store\n(sales_quarantine.csv)"]
    end

    subgraph Data Warehouse (Star Schema)
        Transform --> Loader["Loader Script\n(db/load_data.py)"]
        Loader --> DimCust[("dim_customers")]
        Loader --> DimProd[("dim_products")]
        Loader --> FactSales[("fact_sales")]
    end

    subgraph Analytics & Serving
        DimCust & DimProd & FactSales --> SQL["SQL Analytics\n(db/analytics.py)"]
        SQL --> FastAPI["FastAPI Backend\n(:8000)"]
    end

    subgraph Presentation Layer
        FastAPI <-->|REST API| React["React 19 Dashboard\n(:5173)"]
    end
```

---

## ✨ Key Features & Technical Highlights

1. **Robust Ingestion & Schema Validation**:
   * Validates required columns, primary key completeness, and domain ranges.
   * Quarantines corrupted records (e.g. negative quantities, unknown status enums) into [`data/processed/sales_quarantine.csv`](data/processed/sales_quarantine.csv) while allowing clean transactions to proceed.
2. **Feature Engineering & Imputation**:
   * Automatically imputes non-critical missing values (e.g., synthetic placeholder emails).
   * Derives calendar dimensions (`order_year`, `order_month`, `order_quarter`, `order_day_name`).
   * Computes financial metrics: `gross_amount`, `discount_amount`, `net_amount`, `estimated_cogs` (65% COGS model), `estimated_profit`, and `profit_margin_pct`.
3. **Relational Star Schema Warehouse**:
   * Normalized `dim_customers` and `dim_products` dimension tables with primary keys.
   * `fact_sales` transactional fact table with foreign keys and composite indexes (`order_date`, `customer_id`, `status`).
   * Dual-database compatibility: Zero-setup local SQLite fallback with instant PostgreSQL switch via `DATABASE_URL`.
4. **Advanced SQL Analytics**:
   * Multi-table JOINs, conditional aggregations, and window functions (`RANK()`, `SUM() OVER ()` for running cumulative revenue).
5. **High-Performance FastAPI Backend**:
   * Auto-documented REST API with Swagger docs at [`http://localhost:8000/docs`](http://localhost:8000/docs).
   * CORS enabled for seamless React integration.
6. **Modern React 19 Dashboard**:
   * Built with Vite. Responsive glassmorphism interface, interactive SVG monthly trend chart, regional performance meters, top product leaderboards, and payment method health breakdown.

---

## 📁 Repository Structure

```text
DataPulse/
├── backend/                  # FastAPI REST API service
│   ├── __init__.py
│   └── main.py              # Endpoints: /api/kpis, /api/trends, /api/dashboard
├── data/
│   ├── raw/                 # Raw datasets (sales_data_raw.csv)
│   └── processed/           # Cleaned (sales_clean.csv) & quarantine artifacts
├── db/                      # Database modeling & analytical queries
│   ├── analytics.py         # Analytical SQL execution engine
│   ├── analytics_queries.sql# ANSI SQL query library
│   ├── connection.py        # SQLite / PostgreSQL connection manager
│   ├── load_data.py         # Star schema automated loader
│   ├── models.py            # SQLAlchemy Declarative models
│   └── schema.sql           # Pure SQL DDL schema & views
├── docs/                    # Architecture & deployment guides
│   ├── ARCHITECTURE.md      # Detailed technical specification
│   └── DEPLOYMENT.md        # ₹0 cloud deployment guide (Vercel, Render, Supabase)
├── etl/                     # Python ETL pipelines
│   ├── generate_sample_data.py
│   ├── ingest.py            # Raw data loader & memory profiling
│   ├── transform.py         # Cleansing & financial feature engineering
│   └── validate.py          # Data validation & quarantining
├── frontend/                # React 19 + Vite dashboard
│   ├── src/
│   │   ├── App.jsx          # Dashboard UI & chart visualizations
│   │   ├── App.css          # Glassmorphism styling
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── scripts/                 # Utility scripts
│   └── run_tests.py         # Unified test runner
├── tests/                   # Automated Pytest test suite (26 tests)
│   ├── test_analytics.py
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_transform.py
│   └── test_validation.py
├── .env.example             # Configuration template
├── .gitignore               # Strict exclusion rules (.venv, *.db, node_modules)
├── docker-compose.yml       # Local multi-service orchestration
├── Dockerfile.backend       # Multi-stage Python container
├── Dockerfile.frontend      # Multi-stage Node/Nginx container
└── requirements.txt         # Pinned Python dependencies
```

---

## ⚡ Quickstart Guide

### 1. Setup Python Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the ETL Pipeline & Load Database
```powershell
# Ingest, validate, and transform raw data into data/processed/
python -m etl.transform

# Populate relational database (data/datapulse.db)
python -m db.load_data
```

### 3. Launch the Backend API
```powershell
python -m uvicorn backend.main:app --reload --port 8000
```
* **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Launch the Frontend Dashboard
```powershell
cd frontend
npm install
npm run dev
```
* **Dashboard URL**: [http://localhost:5173](http://localhost:5173)

### 5. Run Quality Assurance Suite
```powershell
python scripts/run_tests.py
```

---

## 📊 Analytical Insights Snapshot

* **Total Orders**: 148 transactions across 10 customers and 10 products
* **Delivered Orders**: 97 (65.5% fulfillment rate)
* **Total Net Revenue**: ₹1,512,963.40
* **Total Net Profit**: ₹408,097.30 (26.97% overall profit margin)
* **Average Order Value (AOV)**: ₹10,222.73
* **Top Product**: Ultra-HD 4K Monitor 27-inch (₹330,225.00 across 21 units)
* **Top Region**: South (₹347,171.40 revenue with 26.83% profit margin)

---

## 🚀 Development Roadmap

- [x] **Phase 1**: Environment setup and project structure
- [x] **Phase 2**: Import and validate sales data using Python & Pandas
- [x] **Phase 3**: Clean and transform the data
- [x] **Phase 4**: Store the processed data in PostgreSQL / Relational DB
- [x] **Phase 5**: Build SQL analytics
- [x] **Phase 6**: Create a dashboard using React
- [x] **Phase 7**: Connect dashboard to FastAPI backend
- [x] **Phase 8**: Testing, documentation, and deployment preparation
- [ ] **Phase 9**: AI assistant as an advanced feature (Free Local Natural Language Assistant)

# iSpark Inno - Attendance Tracker

A full-stack application developed for the iSpark Inno technical assessment. The system manages technical training programs, cohorts, trainers, trainees, and class attendance using a decoupled architecture with a RESTful backend and an interactive frontend.

## 🛠 Technology Stack
* **Backend:** FastAPI (Python)
* **Database:** PostgreSQL (v18) via `psycopg` (Raw SQL, connection pooling)
* **Data Validation:** Pydantic
* **Frontend:** Streamlit
* **Package Management:** `uv`

## ✨ Core Features
* **Program & Cohort Management:** Create training tracks and assign timeline-specific cohorts.
* **User Management:** Manage Trainer and Trainee profiles with secure database-level constraints to prevent duplicate emails and enforce valid assignments.
* **Class Scheduling:** Schedule classes and assign authorized trainers.
* **Batch Attendance:** Submit complete class attendance rosters at once. Utilizes a PostgreSQL "Upsert" (`ON CONFLICT DO UPDATE`) to handle initial recordings and subsequent corrections safely in a single endpoint.
* **Analytics & Reporting:** 
  * Cohort Reports with calculated attendance rates and sub-75% flagging.
  * Individual Trainee histories ordered by date.
  * Class Summaries showing status aggregates and pending unmarked trainees.

## 📋 Prerequisites
* Python 3.10+
* PostgreSQL server running locally or via a cloud provider
* `uv` package manager (`pip install uv`)

## 🚀 Setup & Installation

**1. Navigate to the project directory:**
```bash
cd "attendance tracker"

# iSpark Inno - Attendance Tracker API & Dashboard

A full-stack application developed for the iSpark Inno technical assessment. The system manages technical training programs, cohorts, trainers, trainees, and class attendance using a decoupled architecture with a RESTful backend and an interactive frontend.

## 🛠 Technology Stack
* **Backend:** FastAPI (Python)
* **Database:** PostgreSQL (v18)
* **Database Driver:** `psycopg` (using raw parameterized SQL and connection pooling)
* **Data Validation:** Pydantic
* **Frontend:** Streamlit
* **Package Management:** `uv` (for fast dependency resolution)

---

## 📋 1. System Prerequisites

Before cloning and running this project, ensure your machine has the following installed:
1. **Python 3.10+**
2. **PostgreSQL:** Installed and running locally (e.g., PostgreSQL 18 via pgAdmin).
3. **`uv` Package Manager:** 
   Open your terminal and install `uv` globally if you do not have it:
   ```bash
   pip install uv
   ```

---

## 🗄️ 2. Database Setup

The application requires an empty PostgreSQL database to connect to before it can build its tables.

1. Open **pgAdmin** (or your terminal `psql`).
2. Create a new, empty database named exactly: `ispark_attendance`
3. In the root directory of this project, create a new file named exactly **`.env`**.
4. Open the `.env` file and paste the following line, replacing `YOUR_PASSWORD` with your actual PostgreSQL password and adjusting the port (e.g., `5432` or `5434`) if necessary:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5434/ispark_attendance
   ```

---

## 📦 3. Project Installation

Open your terminal, navigate to the project directory, and use `uv` to automatically resolve and install all project dependencies into an isolated environment:

```bash
uv add fastapi uvicorn psycopg psycopg-pool pydantic[email] python-dotenv streamlit requests
```

---

## 🏗️ 4. Database Initialization & Seeding

Execute the following commands to construct the database schema and populate it with the assessment's required dummy data. 

**Step 4.1: Initialize the Schema**
This reads `schema.sql` to build tables, enums, relationships, and constraints.
```bash
uv run python init_db.py
```
> *Expected output: "Schema applied successfully! All tables created."*

**Step 4.2: Load the Seed Data**
This populates the database with exactly 2 Programs, 3 Cohorts, 3 Trainers, 15 Trainees, and sample scheduled classes.
```bash
uv run python seed.py
```
> *Expected output: "Seed data successfully loaded!"*

---

## 🚀 5. Running the Application

This is a decoupled system. The Backend (FastAPI) and Frontend (Streamlit) must be run concurrently in **two separate terminal windows**.

### Terminal 1: Start the FastAPI Backend
In your current terminal, start the API server:
```bash
uv run python main.py
```
* **API Interactive Docs (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Terminal 2: Start the Streamlit Frontend
Open a **new, second terminal window** in the project root and run:
```bash
uv run streamlit run frontend.py
```
* **Frontend Dashboard:** http://localhost:8501 (This automatically opens in your browser).

---

## 🧪 6. Feature Walkthrough & Verification

Use the Streamlit Dashboard (http://localhost:8501) to visually test and verify all assessment requirements:

1. **Programs (Req #1):** Navigate to *Programs* to view seeded tracks or create new ones.
2. **Cohorts (Req #2):** Navigate to *Cohorts*. Select a program to view its specific cohorts. The database strictly enforces that `End Date` must be later than `Start Date`.
3. **Trainers & Trainees (Req #3 & #4):** Navigate to *Trainers & Trainees*. Assign existing trainees to new cohorts without duplicating their profiles. Database constraints prevent duplicate emails and double-enrollments.
4. **Classes & Attendance (Req #5, #6, #7):** Navigate to *Classes & Attendance*. Select a cohort, schedule a class, and open the attendance tab. Submit a batch attendance roster. 
   * **Testing the Upsert:** If you change a student's status and submit again, the database uses a seamless `ON CONFLICT DO UPDATE` (Upsert) to safely correct the record without duplicating it.
5. **Reports (Req #8, #9, #10):** Navigate to *Reports*. View the Cohort Report (with a custom calculated attendance rate flagging < 75%), check a single Trainee's chronological history, or pull a Class Summary to see exactly who has not been marked yet.

---

## 📁 7. Project Structure

```text
ispark_attendance/
├── main.py          # FastAPI application, dependency injection, and routing logic
├── database.py      # PostgreSQL connection pooling setup
├── schemas.py       # Pydantic models for strict JSON request/response validation
├── frontend.py      # Streamlit interactive frontend dashboard
├── init_db.py       # Python script to execute DDL database initialization
├── schema.sql       # Raw SQL DDL statements (Tables, Enums, Constraints, Indexes)
├── seed.py          # Script generating the required dummy data via executemany()
├── .env             # Environment variables mapping (Not tracked in git)
├── DESIGN.md        # Architectural decisions and business logic documentation
└── README.md        # Setup and execution instructions
```

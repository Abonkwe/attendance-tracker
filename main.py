from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
import database
import schemas

# 1. The Lifespan Manager
# This tells FastAPI what to do when the server turns on and turns off.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- ON STARTUP ---
    print("Starting up: Opening Database Connection Pool...")
    database.pool = ConnectionPool(conninfo=database.DATABASE_URL)
    
    yield # This means "Let the FastAPI app run now"
    
    # --- ON SHUTDOWN ---
    print("Shutting down: Closing Database Connection Pool...")
    if database.pool:
        database.pool.close()

# 2. Initialize the FastAPI app
app = FastAPI(
    title="iSpark Attendance API", 
    description="API for managing cohorts, trainers, and student attendance.",
    lifespan=lifespan
)

@app.get("/")
def test_database_connection(db = Depends(database.get_db)):
    """
    Test endpoint to verify our database connection is working inside FastAPI.
    """
   
    with db.cursor() as cur:
        
        cur.execute("SELECT name, description FROM programs;")
        
        # Fetch all results from the query
        programs_from_db = cur.fetchall()
        
    return {
        "message": "Database connection successful!",
        "programs_found": programs_from_db
    }



@app.post("/programs", response_model=schemas.ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(program: schemas.ProgramCreate, db = Depends(database.get_db)):
    """
    Create a new Program.
    - We expect 'name' and 'description' in the JSON body.
    - Pydantic ensures 'name' is not empty and is under 150 characters.
    """
    try:
        with db.cursor(row_factory=dict_row) as cur:
            # We use RETURNING to instantly get the newly generated ID and Timestamp back
            cur.execute(
                """
                INSERT INTO programs (name, description) 
                VALUES (%s, %s) 
                RETURNING id, name, description, created_at
                """,
                (program.name, program.description)
            )
            
            new_program = cur.fetchone()
            
            db.commit()
            
            return new_program
            
    # Handle the case where they try to create a program that already exists
    except Exception as e:
        # Always rollback on an error so the connection doesn't get stuck
        db.rollback() 
        # Check if the error is our 'unique' constraint failing
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="A program with this name already exists.")
        # If it's some other error, print it and return a 500
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/programs", response_model=list[schemas.ProgramResponse])
def list_programs(db = Depends(database.get_db)):
    """
    Get a list of all Programs.
    """
    with db.cursor(row_factory=dict_row) as cur:
        # We want to order them by when they were created
        cur.execute("SELECT id, name, description, created_at FROM programs ORDER BY created_at ASC")
        programs = cur.fetchall()
        
    return programs


# ==========================================
# 2. COHORTS ENDPOINTS
# ==========================================

@app.post("/cohorts", response_model=schemas.CohortResponse, status_code=status.HTTP_201_CREATED)
def create_cohort(cohort: schemas.CohortCreate, db = Depends(database.get_db)):
    """
    Create a new Cohort under a specific Program.
    """
    try:
        with db.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO cohorts (program_id, name, start_date, end_date) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id, program_id, name, start_date, end_date, created_at
                """,
                (cohort.program_id, cohort.name, cohort.start_date, cohort.end_date)
            )
            new_cohort = cur.fetchone()
            db.commit()
            return new_cohort
            
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        
        # Here we catch the database constraints and turn them into user-friendly errors!
        if "foreign key constraint" in error_msg:
            raise HTTPException(status_code=400, detail="The specified program_id does not exist.")
        elif "unique constraint" in error_msg:
            raise HTTPException(status_code=400, detail="A cohort with this name already exists in this program.")
        elif "chk_cohort_dates" in error_msg:
            # Enforcing Business Rule 6: Dates make sense
            raise HTTPException(status_code=400, detail="End date must be after the start date.")
        else:
            print(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/programs/{program_id}/cohorts", response_model=list[schemas.CohortResponse])
def list_cohorts_for_program(program_id: int, db = Depends(database.get_db)):
    """
    List all cohorts belonging to a specific program.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, program_id, name, start_date, end_date, created_at 
            FROM cohorts 
            WHERE program_id = %s 
            ORDER BY start_date DESC
            """,
            (program_id,)
        )
        cohorts = cur.fetchall()
        
    return cohorts


@app.get("/cohorts/{cohort_id}", response_model=schemas.CohortResponse)
def get_cohort(cohort_id: int, db = Depends(database.get_db)):
    """
    View details of a single cohort.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, program_id, name, start_date, end_date, created_at 
            FROM cohorts 
            WHERE id = %s
            """,
            (cohort_id,)
        )
        cohort = cur.fetchone()
        
    # If the database returns nothing, send a 404 Not Found error
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found.")
        
    return cohort


# ==========================================
# 3. TRAINERS ENDPOINTS
# ==========================================

@app.post("/trainers", response_model=schemas.TrainerResponse, status_code=status.HTTP_201_CREATED)
def create_trainer(trainer: schemas.TrainerCreate, db = Depends(database.get_db)):
    """Create a new trainer profile."""
    try:
        with db.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "INSERT INTO trainers (name, email) VALUES (%s, %s) RETURNING id, name, email, created_at",
                (trainer.name, trainer.email)
            )
            new_trainer = cur.fetchone()
            db.commit()
            return new_trainer
    except Exception as e:
        db.rollback()
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="A trainer with this email already exists.")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/cohorts/{cohort_id}/trainers", status_code=status.HTTP_201_CREATED)
def assign_trainer_to_cohort(cohort_id: int, assignment: schemas.TrainerAssign, db = Depends(database.get_db)):
    """Assign an existing trainer to a cohort."""
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO cohort_trainers (cohort_id, trainer_id) VALUES (%s, %s)",
                (cohort_id, assignment.trainer_id)
            )
            db.commit()
            return {"message": f"Trainer {assignment.trainer_id} successfully assigned to cohort {cohort_id}."}
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        if "unique constraint" in error_msg:
            raise HTTPException(status_code=400, detail="Trainer is already assigned to this cohort.")
        elif "foreign key" in error_msg:
            raise HTTPException(status_code=400, detail="Invalid cohort_id or trainer_id.")
        raise HTTPException(status_code=500, detail="Internal server error")

# ==========================================
# 4. TRAINEES ENDPOINTS
# ==========================================

@app.post("/trainees", response_model=schemas.TraineeResponse, status_code=status.HTTP_201_CREATED)
def create_trainee(trainee: schemas.TraineeCreate, db = Depends(database.get_db)):
    """Create a new trainee profile."""
    try:
        with db.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "INSERT INTO trainees (name, email) VALUES (%s, %s) RETURNING id, name, email, created_at",
                (trainee.name, trainee.email)
            )
            new_trainee = cur.fetchone()
            db.commit()
            return new_trainee
    except Exception as e:
        db.rollback()
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="A trainee with this email already exists.")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/cohorts/{cohort_id}/enrollments", status_code=status.HTTP_201_CREATED)
def enroll_trainee_in_cohort(cohort_id: int, enrollment: schemas.TraineeEnroll, db = Depends(database.get_db)):
    """Enroll an existing trainee into a cohort."""
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO enrollments (cohort_id, trainee_id) VALUES (%s, %s)",
                (cohort_id, enrollment.trainee_id)
            )
            db.commit()
            return {"message": f"Trainee {enrollment.trainee_id} successfully enrolled in cohort {cohort_id}."}
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        if "unique constraint" in error_msg:
            raise HTTPException(status_code=400, detail="Trainee is already enrolled in this cohort.")
        elif "foreign key" in error_msg:
            raise HTTPException(status_code=400, detail="Invalid cohort_id or trainee_id.")
        raise HTTPException(status_code=500, detail="Internal server error")



# ==========================================
# 5. CLASSES ENDPOINTS
# ==========================================

@app.post("/cohorts/{cohort_id}/classes", response_model=schemas.ClassResponse, status_code=status.HTTP_201_CREATED)
def schedule_class(cohort_id: int, class_data: schemas.ClassCreate, db = Depends(database.get_db)):
    """Schedule a class for a cohort."""
    try:
        with db.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO classes (cohort_id, trainer_id, date, topic) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id, cohort_id, trainer_id, date, topic, created_at
                """,
                (cohort_id, class_data.trainer_id, class_data.date, class_data.topic)
            )
            new_class = cur.fetchone()
            db.commit()
            return new_class
    except Exception as e:
        db.rollback()
        # Enforces Rule 3: The database composite foreign key will reject this 
        # if the trainer is not assigned to the cohort!
        if "foreign key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Trainer is not assigned to this cohort.")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/cohorts/{cohort_id}/classes", response_model=list[schemas.ClassResponse])
def list_cohort_classes(cohort_id: int, db = Depends(database.get_db)):
    """List a cohort's classes by date."""
    with db.cursor(row_factory=dict_row) as cur:
        # Rule: List classes by date
        cur.execute(
            """
            SELECT id, cohort_id, trainer_id, date, topic, created_at 
            FROM classes 
            WHERE cohort_id = %s 
            ORDER BY date ASC
            """,
            (cohort_id,)
        )
        return cur.fetchall()




# ==========================================
# 6 & 7. ATTENDANCE ENDPOINTS
# ==========================================

@app.post("/classes/{class_id}/attendance")
def record_attendance(class_id: int, submission: schemas.BulkAttendanceSubmit, db = Depends(database.get_db)):
    """
    Record OR Correct attendance for a class in a single submission.
    """
    try:
        with db.cursor() as cur:
            # Only assigned trainers can record attendance
            cur.execute("""
                SELECT 1 FROM classes c 
                JOIN cohort_trainers ct ON c.cohort_id = ct.cohort_id 
                WHERE c.id = %s AND ct.trainer_id = %s
            """, (class_id, submission.recorded_by_trainer_id))
            
            if not cur.fetchone():
                raise HTTPException(status_code=403, detail="Trainer is not authorized to record attendance for this class.")
            
         
            # Get a list of valid trainee IDs for this specific class's cohort
            cur.execute("""
                SELECT trainee_id FROM enrollments 
                WHERE cohort_id = (SELECT cohort_id FROM classes WHERE id = %s)
            """, (class_id,))
            valid_trainees = {row[0] for row in cur.fetchall()}
            
            # Check the incoming data against valid enrolled trainees
            attendance_data = []
            for record in submission.records:
                if record.trainee_id not in valid_trainees:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Trainee {record.trainee_id} is not enrolled in this cohort."
                    )
                attendance_data.append((
                    class_id, record.trainee_id, record.status.value, submission.recorded_by_trainer_id
                ))
            

            # If the record doesn't exist, it INSERTs and if it already exists it (on conflict), it updates the status and timestamp.
            cur.executemany("""
                INSERT INTO attendance_records (class_id, trainee_id, status, recorded_by_trainer_id, updated_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (class_id, trainee_id) 
                DO UPDATE SET 
                    status = EXCLUDED.status,
                    recorded_by_trainer_id = EXCLUDED.recorded_by_trainer_id,
                    updated_at = CURRENT_TIMESTAMP
            """, attendance_data)
            
            db.commit()
            return {"message": f"Successfully recorded/updated attendance for {len(attendance_data)} trainees."}
            
    except HTTPException:
        db.rollback()
        raise # Rethrow our custom 400/403 errors
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



# ==========================================
# 8, 9 & 10. REPORTS ENDPOINTS
# ==========================================

@app.get("/cohorts/{cohort_id}/report", response_model=list[schemas.TraineeReport])
def get_cohort_report(cohort_id: int, db = Depends(database.get_db)):
    """
    Requirement #8: Cohort Report.
    Shows every trainee, their status counts, attendance rate, and flags < 75%.
    """
    with db.cursor(row_factory=dict_row) as cur:
        # SQL to get the counts for every student enrolled in the cohort
        cur.execute("""
            SELECT 
                t.id AS trainee_id,
                t.name AS trainee_name,
                COUNT(a.id) FILTER (WHERE a.status = 'Present') AS present_count,
                COUNT(a.id) FILTER (WHERE a.status = 'Absent') AS absent_count,
                COUNT(a.id) FILTER (WHERE a.status = 'Late') AS late_count,
                COUNT(a.id) FILTER (WHERE a.status = 'Excused') AS excused_count
            FROM trainees t
            JOIN enrollments e ON t.id = e.trainee_id
            LEFT JOIN attendance_records a ON a.trainee_id = t.id 
                AND a.class_id IN (SELECT id FROM classes WHERE cohort_id = %s)
            WHERE e.cohort_id = %s
            GROUP BY t.id, t.name
        """, (cohort_id, cohort_id))
        
        raw_results = cur.fetchall()

    reports = []
    for row in raw_results:
        # Calculate totals
        total_marked = row['present_count'] + row['absent_count'] + row['late_count'] + row['excused_count']
        
        # Our Custom Formula: Late is worth 0.5 of a presence. 
        # Excused classes are removed from the total expectation completely.
        expected_classes = total_marked - row['excused_count']
        
        if expected_classes > 0:
            score = row['present_count'] + (row['late_count'] * 0.5)
            rate = (score / expected_classes) * 100
        else:
            rate = 100.0 # If they have no classes or only excused classes, they are at 100%
            
        rate = round(rate, 2)
        
        reports.append({
            **row,
            "total_classes_marked": total_marked,
            "attendance_rate_percentage": rate,
            "is_flagged": rate < 75.0
        })
        
    return reports

@app.get("/cohorts/{cohort_id}/trainees/{trainee_id}/history", response_model=list[schemas.TraineeHistoryRecord])
def get_trainee_history(cohort_id: int, trainee_id: int, db = Depends(database.get_db)):
    """Requirement #9: Trainee history for one cohort in date order."""
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute("""
            SELECT c.id AS class_id, c.date, c.topic, a.status
            FROM classes c
            LEFT JOIN attendance_records a ON c.id = a.class_id AND a.trainee_id = %s
            WHERE c.cohort_id = %s
            ORDER BY c.date ASC
        """, (trainee_id, cohort_id))
        return cur.fetchall()

@app.get("/classes/{class_id}/summary", response_model=schemas.ClassSummary)
def get_class_summary(class_id: int, db = Depends(database.get_db)):
    """Requirement #10: Class summary (status counts and unmarked trainees)."""
    with db.cursor(row_factory=dict_row) as cur:
        # Get the cohort_id for this class
        cur.execute("SELECT cohort_id FROM classes WHERE id = %s", (class_id,))
        class_info = cur.fetchone()
        if not class_info:
            raise HTTPException(status_code=404, detail="Class not found")
            
        cohort_id = class_info['cohort_id']

        # Get status counts
        cur.execute("""
            SELECT status, COUNT(*) as count 
            FROM attendance_records 
            WHERE class_id = %s 
            GROUP BY status
        """, (class_id,))
        
        status_counts = {row['status']: row['count'] for row in cur.fetchall()}

        # Find who is enrolled but HAS NOT been marked for this class
        cur.execute("""
            SELECT t.name
            FROM enrollments e
            JOIN trainees t ON e.trainee_id = t.id
            WHERE e.cohort_id = %s
            AND t.id NOT IN (
                SELECT trainee_id FROM attendance_records WHERE class_id = %s
            )
        """, (cohort_id, class_id))
        
        unmarked = [row['name'] for row in cur.fetchall()]

    return {
        "class_id": class_id,
        "status_counts": status_counts,
        "unmarked_trainees": unmarked
    }




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
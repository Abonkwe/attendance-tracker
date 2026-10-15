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
        # We tell psycopg to return rows as dictionaries (perfect for APIs)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
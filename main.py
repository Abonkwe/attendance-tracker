from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from psycopg_pool import ConnectionPool
import database

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
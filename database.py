import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

# Load the environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# We create an empty variable for our pool. 
# We will fill it when the FastAPI server actually starts.
pool = None

def get_db():
    """
    This is our FastAPI 'Dependency'.
    Whenever a route needs to talk to the database, it calls this function.
    It grabs an open connection from the pool, 'yields' it to the route, 
    and automatically returns it to the pool when the route finishes.
    """
    # Fetch a connection from the pool
    with pool.connection() as conn:
        yield conn
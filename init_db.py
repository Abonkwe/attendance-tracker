import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def init_database():
    if not DATABASE_URL:
        print("Error: DATABASE_URL is not set in .env")
        return

    schema_file = Path("schema.sql")
    if not schema_file.exists():
        print("Error: schema.sql not found in current directory")
        return

    print("Connecting to PostgreSQL on port 5434...")
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                with open(schema_file, "r", encoding="utf-8") as f:
                    cur.execute(f.read())
            conn.commit()
        print("Schema applied successfully! All tables created.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")


if __name__ == "__main__":
    init_database()
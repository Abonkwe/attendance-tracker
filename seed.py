import os
import psycopg
from dotenv import load_dotenv
from datetime import date

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def seed_database():
    print("Connecting to database...")
    
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:

                # programs data
                print("Adding Programs...")
                programs_data = [
                    ('Backend Engineering', 'Learn servers and databases'),
                    ('Frontend Engineering', 'Learn web interfaces')
                ]
                cur.executemany(
                    "INSERT INTO programs (name, description) VALUES (%s, %s)", 
                    programs_data
                )

               # cohorts data
                print("Adding Cohorts...")
                cohorts_data = [
                    # program_id, name, start_date, end_date
                    (1, 'Backend Cohort 1', date(2027, 1, 1), date(2027, 3, 1)),
                    (1, 'Backend Cohort 2', date(2027, 4, 1), date(2027, 6, 1)),
                    (2, 'Frontend Cohort 1', date(2027, 1, 1), date(2027, 3, 1))
                ]
                cur.executemany(
                    "INSERT INTO cohorts (program_id, name, start_date, end_date) VALUES (%s, %s, %s, %s)", 
                    cohorts_data
                )

                #trainers data
                print("Adding Trainers...")
                trainers_data = [
                    ('Abonkwe', 'abonkwe@ispark.com'),    # id 1
                    ('Princely', 'princely@ispark.com'),        # id 2 
                    ('Atanga', 'atanga@ispark.com')  # id 3
                ]
                cur.executemany(
                    "INSERT INTO trainers (name, email) VALUES (%s, %s)", 
                    trainers_data
                )

                # assign trainers to cohors. one of whom teaches in two cohorts of different programs
             
                print("Assigning Trainers to Cohorts...")
                cohort_trainers_data = [
                    (1, 1), # Cohort 1 (Backend), Trainer 1 (Abonkwe)
                    (3, 1), # Cohort 3 (Frontend), Trainer 1 (Abonkwe) -> meets reruirement
                    (2, 2), # Cohort 2 (Backend), Trainer 2 (Princely)
                    (3, 3)  # Cohort 3 (Frontend), Trainer 3 (Atanga)
                ]
                cur.executemany(
                    "INSERT INTO cohort_trainers (cohort_id, trainer_id) VALUES (%s, %s)", 
                    cohort_trainers_data
                )

                # trainees data. data is generated dynamically for 15 trainees
                print("Adding 15 Trainees...")

                trainees_data = [(f"Student {i}", f"student{i}@ispark.com") for i in range(1, 16)]
                cur.executemany(
                    "INSERT INTO trainees (name, email) VALUES (%s, %s)", 
                    trainees_data
                )

                # enrollments data. one of whom is enrolled in two cohorts of different programs
                print("Enrolling Trainees...")
                enrollments_data = [
                    (1, 1), # Student 1 in Cohort 1
                    (3, 1), # Student 1 in Cohort 3 -> MEETS REQUIREMENT
                ]
                
                # Add Students 2-6 to Cohort 1
                enrollments_data += [(1, i) for i in range(2, 7)]
                # Add Students 7-11 to Cohort 2
                enrollments_data += [(2, i) for i in range(7, 12)]
                # Add Students 12-15 to Cohort 3
                enrollments_data += [(3, i) for i in range(12, 16)]

                cur.executemany(
                    "INSERT INTO enrollments (cohort_id, trainee_id) VALUES (%s, %s)", 
                    enrollments_data
                )

                # classes data. atleast four per cohort, with one of the classes taught by a trainer who teaches in two different cohorts
                print("Adding Classes...")
                classes_data = [
                    # Backend 1 (cohort_id, trainer_id, date, topic)
                    (1, 1, date(2027, 1, 5), "Python Intro"), (1, 1, date(2027, 1, 10), "Lists"),
                    (1, 1, date(2027, 1, 15), "Loops"), (1, 1, date(2027, 1, 20), "Dictionaries"),
                    
                    # Backend 2
                    (2, 2, date(2027, 4, 5), "SQL Intro"), (2, 2, date(2027, 4, 10), "Selects"),
                    (2, 2, date(2027, 4, 15), "Joins"), (2, 2, date(2027, 4, 20), "Group By"),
                    
                    # Frontend 1 (Taught by both Alice and Charlie)
                    (3, 1, date(2027, 1, 6), "HTML"), (3, 1, date(2027, 1, 11), "CSS"),
                    (3, 3, date(2027, 1, 16), "JavaScript"), (3, 3, date(2027, 1, 21), "React")
                ]
                cur.executemany(
                    "INSERT INTO classes (cohort_id, trainer_id, date, topic) VALUES (%s, %s, %s, %s)", 
                    classes_data
                )

                # ==========================================
                # 8. ATTENDANCE (Bulk inserting dynamically generated records)
                # ==========================================
                print("Marking Attendance...")
                
                # Fetch all classes we just created
                cur.execute("SELECT id, cohort_id, trainer_id FROM classes")
                all_classes = cur.fetchall()
                
                attendance_data = [] # We will fill this list, then execute it all at once
                
                for class_id, cohort_id, trainer_id in all_classes:
                    # Find all students enrolled in this cohort
                    cur.execute("SELECT trainee_id FROM enrollments WHERE cohort_id = %s", (cohort_id,))
                    enrolled_students = cur.fetchall()
                    
                    # Create an attendance record for every enrolled student
                    for index, (student_id,) in enumerate(enrolled_students):
                        # Simple logic to create diverse statuses (Present, Late, Excused)
                        status = 'Present'
                        if index == 0: status = 'Late'
                        elif index == 1: status = 'Excused'
                            
                        # Add the tuple to our bulk list
                        attendance_data.append((class_id, student_id, status, trainer_id))
                
                # Run the massive bulk insert with one command
                cur.executemany("""
                    INSERT INTO attendance_records (class_id, trainee_id, status, recorded_by_trainer_id) 
                    VALUES (%s, %s, %s, %s)
                """, attendance_data)

            # Save (commit) all changes
            conn.commit()
            print("Seed data successfully loaded!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    seed_database()
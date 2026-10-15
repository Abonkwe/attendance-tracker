from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from enum import Enum


class AttendanceStatus(str, Enum):
    Present = 'Present'
    Absent = 'Absent'
    Late = 'Late'
    Excused = 'Excused'
  
  
# data user sends to us when creating a new program
class ProgramCreate(BaseModel):
    name: str = Field(..., max_length=150, description="Name of the training program")
    description: str | None = Field(None, description="Optional description of the program")

# what we send back to the user after creating a new program
class ProgramResponse(ProgramCreate):
    id: int
    created_at: datetime

#cohorts
class CohortCreate(BaseModel):
    program_id: int
    name: str = Field(..., max_length=150)
    start_date: date
    end_date: date

class CohortResponse(CohortCreate):
    id: int
    created_at: datetime

# trainers
class TrainerCreate(BaseModel):
    name: str = Field(..., max_length=150)
    email: EmailStr 

class TrainerResponse(TrainerCreate):
    id: int
    created_at: datetime


#attendance
# For Requirement #6: Record status for trainees in a single submission
class AttendanceRecordCreate(BaseModel):
    trainee_id: int
    status: AttendanceStatus # Pydantic guarantees it will exactly match one of our 4 statuses

class BulkAttendanceSubmit(BaseModel):
    # class_id: int
    recorded_by_trainer_id: int
    records: list[AttendanceRecordCreate]


#trainees
class TraineeCreate(BaseModel):
    name: str = Field(..., max_length=150)
    email: EmailStr

class TraineeResponse(TraineeCreate):
    id: int
    created_at: datetime


#assignments & enrollments
class TrainerAssign(BaseModel):
    trainer_id: int

class TraineeEnroll(BaseModel):
    trainee_id: int


#classes
class ClassCreate(BaseModel):
    trainer_id: int
    date: date
    topic: str | None = None

class ClassResponse(ClassCreate):
    id: int
    cohort_id: int
    created_at: datetime



#reports and summaries
class TraineeReport(BaseModel):
    trainee_id: int
    trainee_name: str
    present_count: int
    absent_count: int
    late_count: int
    excused_count: int
    total_classes_marked: int
    attendance_rate_percentage: float
    is_flagged: bool # True if attendance is below 75%

class TraineeHistoryRecord(BaseModel):
    class_id: int
    date: date
    topic: str | None
    status: AttendanceStatus | None # None if they haven't been marked yet

class ClassSummary(BaseModel):
    class_id: int
    status_counts: dict[str, int]
    unmarked_trainees: list[str] # List of names who haven't been marked
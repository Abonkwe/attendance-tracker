from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from enum import Enum


class AttendanceStatus(str, Enum):
    Present = 'Present'
    Absent = 'Absent'
  
  
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
    email: EmailStr # Pydantic will automatically verify this is a valid email format!

class TrainerResponse(TrainerCreate):
    id: int
    created_at: datetime


#attendance
# For Requirement #6: Record status for trainees in a single submission
class AttendanceRecordCreate(BaseModel):
    trainee_id: int
    status: AttendanceStatus # Pydantic guarantees it will exactly match one of our 4 statuses

class BulkAttendanceSubmit(BaseModel):
    class_id: int
    recorded_by_trainer_id: int
    records: list[AttendanceRecordCreate]
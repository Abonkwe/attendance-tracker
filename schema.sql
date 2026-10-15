DROP TABLE IF EXISTS attendance_records CASCADE;
DROP TABLE IF EXISTS classes CASCADE;
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS cohort_trainers CASCADE;
DROP TABLE IF EXISTS cohorts CASCADE;
DROP TABLE IF EXISTS trainees CASCADE;
DROP TABLE IF EXISTS trainers CASCADE;
DROP TABLE IF EXISTS programs CASCADE;
DROP TYPE IF EXISTS attendance_status CASCADE;

-- 1. Status Enum
CREATE TYPE attendance_status AS ENUM ('Present', 'Absent');

-- 2. Programs
CREATE TABLE programs (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Cohorts
CREATE TABLE cohorts (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    program_id INT NOT NULL REFERENCES programs(id) ON DELETE RESTRICT,
    name VARCHAR(150) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_cohort_dates CHECK (end_date > start_date),
    CONSTRAINT uq_program_cohort_name UNIQUE (program_id, name)
);

-- 4. Trainers
CREATE TABLE trainers (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Cohort Trainers (Many-to-Many junction)
CREATE TABLE cohort_trainers (
    cohort_id INT NOT NULL REFERENCES cohorts(id) ON DELETE RESTRICT,
    trainer_id INT NOT NULL REFERENCES trainers(id) ON DELETE RESTRICT,
    assigned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cohort_id, trainer_id)
);

-- 6. Trainees
CREATE TABLE trainees (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. Enrollments (Many-to-Many junction)
CREATE TABLE enrollments (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cohort_id INT NOT NULL REFERENCES cohorts(id) ON DELETE RESTRICT,
    trainee_id INT NOT NULL REFERENCES trainees(id) ON DELETE RESTRICT,
    enrolled_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cohort_trainee UNIQUE (cohort_id, trainee_id)
);

-- 8. Classes
CREATE TABLE classes (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cohort_id INT NOT NULL REFERENCES cohorts(id) ON DELETE RESTRICT,
    trainer_id INT NOT NULL,
    date DATE NOT NULL,
    topic VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cohort_id, trainer_id) 
        REFERENCES cohort_trainers(cohort_id, trainer_id) 
        ON DELETE RESTRICT
);

-- 9. Attendance Records
CREATE TABLE attendance_records (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    class_id INT NOT NULL REFERENCES classes(id) ON DELETE RESTRICT,
    trainee_id INT NOT NULL REFERENCES trainees(id) ON DELETE RESTRICT,
    status attendance_status NOT NULL,
    recorded_by_trainer_id INT NOT NULL REFERENCES trainers(id) ON DELETE RESTRICT,
    recorded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_class_trainee UNIQUE (class_id, trainee_id)
);

-- Performance Indexes
CREATE INDEX idx_classes_cohort_date ON classes(cohort_id, date);
CREATE INDEX idx_attendance_class ON attendance_records(class_id);
CREATE INDEX idx_attendance_trainee ON attendance_records(trainee_id);
CREATE INDEX idx_enrollments_cohort ON enrollments(cohort_id);
-- ========= CREATE TABLES =========

-- Drop tables in reverse order of dependency if they already exist
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS assignments;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS prerequisites;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS instructors;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- Central table for all user authentication and basic info
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    university_id VARCHAR(50) UNIQUE NOT NULL, -- e.g., SIT student/staff ID
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'instructor', 'admin')),
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

CREATE INDEX idx_users_university_id ON users (university_id);
CREATE INDEX idx_users_role ON users (role);

-- Extends the users table with student-specific data
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    enrollment_year INT NOT NULL,
    major VARCHAR(100),
    expected_graduation VARCHAR(10),
    gpa DECIMAL(3, 2) CHECK (gpa >= 0.0 AND gpa <= 5.0), -- Assuming a 5.0 scale
    current_standing VARCHAR(20) DEFAULT 'Good',
    
    CONSTRAINT fk_student_user
        FOREIGN KEY(student_id) 
        REFERENCES users(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Extends the users table with instructor-specific data
CREATE TABLE instructors (
    instructor_id INT PRIMARY KEY,
    department_code VARCHAR(50) NOT NULL,
    office_location VARCHAR(50),
    office_hours TEXT,
    title VARCHAR(50),

    CONSTRAINT fk_instructor_user
        FOREIGN KEY(instructor_id) 
        REFERENCES users(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table for all courses offered
CREATE TABLE courses (
    course_id VARCHAR(10) PRIMARY KEY, -- Using String ID like "INF2001"
    course_code VARCHAR(10) UNIQUE NOT NULL,
    course_name VARCHAR(150) NOT NULL,
    description TEXT,
    credits INT NOT NULL DEFAULT 3,
    academic_term VARCHAR(20),
    max_capacity INT DEFAULT 30,
    current_enrollment INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    instructor_id INT,

    CONSTRAINT fk_course_instructor
        FOREIGN KEY(instructor_id) 
        REFERENCES instructors(instructor_id)
        ON DELETE SET NULL -- If instructor is deleted, course remains but unassigned
) ENGINE=InnoDB;

CREATE INDEX idx_courses_course_code ON courses (course_code);
CREATE INDEX idx_courses_academic_term ON courses (academic_term);

-- Junction table for course prerequisites
CREATE TABLE prerequisites (
    course_id VARCHAR(10) NOT NULL,
    requires_course_id VARCHAR(10) NOT NULL,
    
    PRIMARY KEY (course_id, requires_course_id),
    
    CONSTRAINT fk_prereq_course
        FOREIGN KEY(course_id) 
        REFERENCES courses(course_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_prereq_requires
        FOREIGN KEY(requires_course_id) 
        REFERENCES courses(course_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Junction table linking students to courses
CREATE TABLE enrollments (
    student_id INT NOT NULL,
    course_id VARCHAR(10) NOT NULL,
    semester VARCHAR(20) NOT NULL, -- e.g., "T1-2025"
    enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    final_grade VARCHAR(2),
    status VARCHAR(20) DEFAULT 'Enrolled' CHECK (status IN ('Enrolled', 'Completed', 'Dropped')),
    
    -- A student can re-take a course, so the PK must include the semester
    PRIMARY KEY (student_id, course_id, semester),
    
    CONSTRAINT fk_enroll_student
        FOREIGN KEY(student_id) 
        REFERENCES students(student_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_enroll_course
        FOREIGN KEY(course_id) 
        REFERENCES courses(course_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_enrollments_status ON enrollments (status);

-- Table for assignments within a course
CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id VARCHAR(10) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATETIME NOT NULL,
    max_score FLOAT NOT NULL DEFAULT 100.0,
    assignment_type VARCHAR(50) CHECK (assignment_type IN ('Quiz', 'Project', 'Milestone', 'Lab', 'Exam')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_assign_course
        FOREIGN KEY(course_id) 
        REFERENCES courses(course_id)
        ON DELETE CASCADE -- If course is deleted, assignments are deleted
) ENGINE=InnoDB;

CREATE INDEX idx_assignments_course_id ON assignments (course_id);
CREATE INDEX idx_assignments_due_date ON assignments (due_date);

-- Table for student submissions for assignments
CREATE TABLE submissions (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL,
    student_id INT NOT NULL,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(255),
    score FLOAT,
    feedback TEXT,
    status VARCHAR(20) DEFAULT 'Submitted' CHECK (status IN ('Submitted', 'Graded', 'Late')),
    
    -- A student should only have one submission per assignment
    UNIQUE(assignment_id, student_id), 
    
    CONSTRAINT fk_submit_assign
        FOREIGN KEY(assignment_id) 
        REFERENCES assignments(assignment_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_submit_student
        FOREIGN KEY(student_id) 
        REFERENCES students(student_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_submissions_status ON submissions (status);

-- ========= INSERT SAMPLE DATA =========

-- 1. Create Users
-- (Passwords are placeholders and should be properly hashed in a real application)
INSERT INTO users (university_id, email, password_hash, first_name, last_name, role)
VALUES
('A0001', 'emily.tan@sit.admin', 'hash_placeholder_admin', 'Emily', 'Tan', 'admin'),
('S0001', 'rajesh.k@sit.edu.sg', 'hash_placeholder_inst1', 'Rajesh', 'Kumar', 'instructor'),
('S0002', 'siti.n@sit.edu.sg', 'hash_placeholder_inst2', 'Siti', 'Nurhaliza', 'instructor'),
('2301111', 'weiming.tan.23@sit.singaporetech.edu.sg', 'hash_placeholder_stud1', 'Wei Ming', 'Tan', 'student'),
('2202222', 'jiayi.lim.22@sit.singaporetech.edu.sg', 'hash_placeholder_stud2', 'Jia Yi', 'Lim', 'student'),
('2303333', 'junjie.ong.23@sit.singgaporetech.edu.sg', 'hash_placeholder_stud3', 'Jun Jie', 'Ong', 'student');

-- 2. Create Instructors (linking to users)
INSERT INTO instructors (instructor_id, department_code, office_location, office_hours, title)
VALUES
(2, 'INF', 'SIT@Dover, D-05-01', 'Mon 10:00-12:00', 'Associate Professor'),
(3, 'BUS', 'SIT@Dover, B-02-05', 'Wed 14:00-16:00', 'Lecturer');

-- 3. Create Students (linking to users)
INSERT INTO students (student_id, enrollment_year, major, expected_graduation, gpa, current_standing)
VALUES
(4, 2023, 'Information and Communications Technology (Software Engineering)', '2026', 3.55, 'Good'),
(5, 2022, 'Information and Communications Technology (Information Security)', '2025', 3.82, 'Good'),
(6, 2023, 'Computer Science in Real-Time Interactive Simulation', '2026', 3.10, 'Good');

-- 4. Create Courses (linking to instructors)
INSERT INTO courses (course_id, course_code, course_name, description, credits, academic_term, max_capacity, instructor_id)
VALUES
('INF2001', 'INF2001', 'Introduction to Software Engineering', 'Covers the fundamentals of software engineering principles and practices.', 5, 'T1-2025', 50, 2),
('INF2003', 'INF2003', 'Database Systems', 'Introduction to database design, implementation, and management.', 5, 'T1-2025', 40, 2),
('ICT1001', 'ICT1001', 'Programming 1', 'Fundamental programming concepts using Python.', 5, 'T3-2024', 100, 2),
('BUS1001', 'BUS1001', 'Introduction to Management', 'Provides an overview of management theories and practices.', 4, 'T1-2025', 60, 3);

-- 5. Define Prerequisites
INSERT INTO prerequisites (course_id, requires_course_id)
VALUES
('INF2001', 'ICT1001'), -- To take INF2001, you must have taken ICT1001
('INF2003', 'ICT1001'); -- To take INF2003, you must have taken ICT1001

-- 6. Enroll Students
INSERT INTO enrollments (student_id, course_id, semester, status, final_grade)
VALUES
(5, 'ICT1001', 'T3-2024', 'Completed', 'A-'), -- Past enrollment
(4, 'INF2001', 'T1-2025', 'Enrolled', NULL),  -- Current enrollments
(4, 'BUS1001', 'T1-2025', 'Enrolled', NULL),
(5, 'INF2003', 'T1-2025', 'Enrolled', NULL),
(6, 'INF2001', 'T1-2025', 'Enrolled', NULL);

-- 7. Create Assignments
INSERT INTO assignments (course_id, title, description, due_date, max_score, assignment_type)
VALUES
('INF2001', 'Project Milestone 1: Requirements', 'Define the functional and non-functional requirements for your team project.', '2025-11-10 23:59:00', 100, 'Project'),
('INF2001', 'Quiz 1: SDLC Models', 'Short quiz on waterfall, agile, and spiral models.', '2025-10-25 17:00:00', 20, 'Quiz'),
('INF2003', 'Lab 2: SQL Queries', 'Complete the 10 SQL query exercises on the provided database.', '2025-11-12 23:59:00', 50, 'Lab');

-- 8. Log Submissions
INSERT INTO submissions (assignment_id, student_id, submitted_at, file_path, score, feedback, status)
VALUES
(1, 4, '2025-11-09 18:30:00', '/uploads/inf2001/wm_tan_req.pdf', NULL, NULL, 'Submitted'),
(1, 6, '2025-11-10 23:50:00', '/uploads/inf2001/jj_ong_req.pdf', NULL, NULL, 'Submitted'), -- Note: This is no longer 'Late' by default, as the due date is 23:59. Changed status to 'Submitted'.
(2, 4, '2025-10-25 14:20:00', NULL, 18.0, 'Good job on the agile definitions.', 'Graded'),
(2, 6, '2025-10-25 14:22:00', NULL, 15.0, 'Review the differences between spiral and waterfall.', 'Graded'),
(3, 5, '2025-11-11 09:15:00', '/uploads/inf2003/jy_lim_lab2.sql', NULL, NULL, 'Submitted');

-- ========= END OF SCRIPT =========
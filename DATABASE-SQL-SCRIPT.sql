/*
=========================================================
INF2003 UCMS - COMPLETE DATABASE CREATION SCRIPT
=========================================================
This script integrates the schema (CREATE TABLE) and the 
final data (INSERT) into one file.

It performs the following actions:
1. Temporarily disables safety checks.
2. Drops all tables if they exist to ensure a clean slate.
3. Re-enables foreign key checks.
4. Creates the complete database schema (users, courses, etc.).
5. Inserts all parent data (Users, Instructors, Students).
6. Inserts all 100+ PDF-accurate courses.
7. Inserts all PDF-accurate prerequisites.
8. Inserts the academic history for the "Alex Cross" student.
9. Updates the enrollment counts for the "Enrolled" courses.
10. Resets safety checks.
=========================================================
*/

/* =========================================================
PART 1: RESET AND CREATE SCHEMA
(Combines safety checks from NEW and DROP/CREATE from OLD)
=========================================================
*/

-- Disable checks to allow dropping tables and running updates
SET SQL_SAFE_UPDATES = 0;
SET FOREIGN_KEY_CHECKS = 0;

-- Drop tables in reverse order of dependency if they already exist
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS assignments;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS prerequisites;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS instructors;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;

-- Re-enable foreign key checks *before* creating tables
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
    semester VARCHAR(20) NOT NULL, -- e.g., "T1-2025" or "Y1T1"
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

/* =========================================================
PART 2: POPULATE DATABASE WITH PDF-ACCURATE DATA
(From NEW DATA script)
=========================================================
*/

/* =========================================================
STEP 4: POPULATE PARENT TABLES (USERS, INSTRUCTORS, STUDENTS)
=========================================================
*/
-- Create Users (Instructors 1-4 and Student 1001)
INSERT INTO users (user_id, university_id, email, password_hash, first_name, last_name, role, date_joined, is_active)
VALUES
(1, 'I-001', 'instructor1@ucms.edu', 'hashed_pass_1', 'Alan', 'Turing', 'instructor', NOW(), 1),
(2, 'I-002', 'instructor2@ucms.edu', 'hashed_pass_2', 'Ada', 'Lovelace', 'instructor', NOW(), 1),
(3, 'I-003', 'instructor3@ucms.edu', 'hashed_pass_3', 'Grace', 'Hopper', 'instructor', NOW(), 1),
(4, 'I-004', 'instructor4@ucms.edu', 'hashed_pass_4', 'Siti', 'Nurhaliza', 'instructor', NOW(), 1),
(5, 'I-005', 'instructor5@ucms.edu', 'hashed_pass_5', 'Azure', 'Bluet', 'instructor', NOW(), 1),
(1001, 'S2401001A', 'alex.student@ucms.edu', 'hashed_pass_s1', 'Alex', 'Cross', 'student', '2024-08-20 10:00:00', 1);

-- Create Instructor Profiles
INSERT INTO instructors (instructor_id, department_code, office_location, office_hours, title)
VALUES
(1, 'CS', 'SIT@Dover, C-01-01', 'Mon/Wed 10-12', 'Professor'),
(2, 'INF', 'SIT@Dover, D-05-01', 'Mon 10:00-12:00', 'Associate Professor'),
(3, 'BUS', 'SIT@Dover, B-02-05', 'Wed 14:00-16:00', 'Lecturer'),
(4, 'GEN', 'SIT@Dover, A-04-01', 'Fri 09:00-11:00', 'Lecturer'),
(5, 'INF', 'SIT@Dover, D-04-01', 'Wed 09:00-11:00', 'Mascot');

-- Create Student Profile (for Alex)
INSERT INTO students (student_id, enrollment_year, major, expected_graduation, gpa, current_standing)
VALUES (1001, 2024, 'BEng (Hons) ICT (Software Engineering)', 2028, 4.0, 'Year 2');

/* =========================================================
STEP 5: POPULATE COURSES TABLE (PDF-ACCURATE)
=========================================================
*/
INSERT IGNORE INTO courses (course_id, course_code, course_name, description, credits, instructor_id, academic_term, max_capacity, current_enrollment)
VALUES
('ICT1011', 'ICT1011', 'Computer Organization & Architecture', 'Fundamentals of computer hardware, architecture, and organization.', 6, 2, 'Fall 2025', 100, 0),
('INF1001', 'INF1001', 'Introduction to Computing', 'An overview of computing, software, hardware, operating systems, and security.', 6, 1, 'Fall 2025', 150, 0),
('INF1002', 'INF1002', 'Programming Fundamentals', 'An introduction to foundational programming concepts using a modern language.', 6, 1, 'Fall 2025', 150, 0),
('INF1003', 'INF1003', 'Mathematics 1', 'Foundational mathematics for computing, including calculus and algebra.', 6, 3, 'Fall 2025', 150, 0),
('UDC1001', 'UDC1001', 'Digital Competency Essentials', 'Essential digital literacy skills for the modern university student and professional.', 2, 4, 'Fall 2025', 200, 0),
('ICT1012', 'ICT1012', 'Operating Systems', 'Principles and design of modern operating systems, including process and memory management.', 6, 2, 'Spring 2026', 100, 0),
('INF1004', 'INF1004', 'Mathematics 2', 'Further topics in mathematics relevant to computing, including discrete mathematics and statistics.', 6, 3, 'Spring 2026', 150, 0),
('INF1005', 'INF1005', 'Web Systems & Technologies', 'Design and development of dynamic web applications, covering front-end and back-end.', 6, 1, 'Spring 2026', 120, 0),
('INF1009', 'INF1009', 'Object-Oriented Programming', 'Principles of OOP, including classes, objects, inheritance, and polymorphism.', 6, 1, 'Spring 2026', 130, 0),
('UCS1001', 'UCS1001', 'Critical Thinking and Communicating', 'Develops skills in critical analysis, logical reasoning, and effective communication.', 4, 4, 'Spring 2026', 200, 0),
('INF1006', 'INF1006', 'Computer Networks', 'Fundamentals of computer networking, TCP/IP protocol suite, and network security basics.', 6, 2, 'Fall 2025', 100, 0),
('INF1007', 'INF1007', 'Ethics and Professional Conduct', 'Ethical and professional responsibilities of an ICT professional.', 6, 4, 'Fall 2025', 150, 0),
('INF1008', 'INF1008', 'Data Structures and Algorithms', 'Core module on the design, analysis, and implementation of data structures and algorithms.', 6, 1, 'Fall 2025', 130, 0),
('INF2001', 'INF2001', 'Introduction to Software Engineering', 'Fundamentals of software engineering principles, practices, and the software development lifecycle.', 6, 1, 'Fall 2025', 100, 0),
('INF2002', 'INF2002', 'Human Computer Interaction', 'Methods and principles for designing, programming, and testing human-centric systems.', 6, 4, 'Fall 2025', 90, 0),
('INF2003', 'INF2003', 'Database Systems', 'Introduction to database design, implementation, and management. Covers relational models, SQL, and NoSQL.', 6, 1, 'Fall 2025', 100, 0),
('INF2004', 'INF2004', 'Embedded Systems Programming', 'Programming embedded systems, computer architectures, and microcontrollers.', 6, 2, 'Fall 2025', 70, 0),
('UDE2222', 'UDE2222', 'Design Innovation', 'An introduction to design thinking principles and innovation processes.', 6, 4, 'Fall 2025', 150, 0),
('ICT2112', 'ICT2112', 'Software Design', 'Covers software design patterns, principles, and architectures for building scalable systems.', 6, 1, 'Spring 2026', 80, 0),
('ICT2113', 'ICT2113', 'Software Modelling and Analysis', 'Techniques for modeling and analyzing software systems using UML and other notations.', 6, 1, 'Spring 2026', 80, 0),
('INF2007', 'INF2007', 'Mobile Application Development', 'Design and development of applications for mobile devices, focusing on Android or iOS.', 6, 1, 'Spring 2026', 90, 0),
('INF2008', 'INF2008', 'Machine Learning', 'Introduction to the concepts and algorithms of machine learning.', 6, 1, 'Spring 2026', 100, 0),
('USI2001', 'USI2001', 'Social Innovation Project', 'A project focused on creating innovative solutions to social problems.', 3, 4, 'Spring 2026', 150, 0),
('ICT2114', 'ICT2114', 'Integrative Team Project', 'A project module where students work in teams to develop a software solution.', 6, 4, 'Fall 2025', 100, 0),
('ICT2216', 'ICT2216', 'Secure Software Development', 'Teaches principles and practices for building secure and robust software.', 6, 1, 'Fall 2025', 80, 0),
('INF2335', 'INF2335', 'Global Learning in ICT Advances', 'Explores advanced and emerging topics in the field of ICT.', 6, 4, 'Fall 2025', 50, 0),
('ICT3219', 'ICT3219', 'Industry Certification Module', 'Preparation for a professional industry certification in cybersecurity or IT.', 6, 4, 'Spring 2026', 100, 0),
('ICT3112', 'ICT3112', 'Software Verification and Validation', 'Techniques for testing, verifying, and validating software to ensure quality.', 6, 1, 'Fall 2025', 60, 0),
('ICT3113', 'ICT3113', 'Performance Testing and Optimisation', 'Methods for testing and optimizing the performance of software applications.', 6, 1, 'Fall 2025', 60, 0),
('ICT3217', 'ICT3217', 'Integrative Team Project 2', 'A second, more advanced project module for teams.', 6, 4, 'Fall 2025', 80, 0),
('INF2005', 'INF2005', 'Cyber Security Fundamentals', 'Introductory course covering basic principles of cybersecurity.', 6, 2, 'Fall 2025', 100, 0),
('ICT2215', 'ICT2215', 'Mobile Security', 'Covers security challenges and defenses for mobile operating systems and applications.', 6, 2, 'Spring 2026', 70, 0),
('INF2006', 'INF2006', 'Cloud Computing and Big Data', 'Fundamentals of cloud computing architectures and big data technologies.', 6, 1, 'Spring 2026', 90, 0),
('INF2009', 'INF2009', 'Edge Computing and Analytics', 'Explores computing and data analytics at the edge of the network.', 6, 2, 'Spring 2026', 60, 0),
('UCM3001', 'UCM3001', 'Change Management', 'A study of the principles and practices for managing organizational change.', 6, 4, 'Spring 2026', 100, 0),
('ICT4011', 'ICT4011', 'Capstone Project', 'A year-long final project to design and develop a significant system.', 5, 4, 'Fall 2025', 150, 0),
('ICT4012B', 'ICT4012B', 'Integrated Work Study Programme (Work Attachment)', 'A long-term work placement in a relevant company.', 10, 4, 'Fall 2025', 150, 0),
('INF1101', 'INF1101', 'Introduction to Computer Systems', 'A broad overview of computer systems, from hardware to software.', 6, 2, 'Fall 2025', 100, 0),
('AAI1001', 'AAI1001', 'Data Engineering and Visualization', 'Techniques for collecting, cleaning, and visualizing large datasets.', 6, 1, 'Fall 2025', 80, 0),
('AAI2007', 'AAI2007', 'Artificial Intelligence in Business and Society', 'Examines the impact of AI on business and societal issues.', 3, 4, 'Fall 2025', 100, 0),
('AAI3001', 'AAI3001', 'Computer Vision and Deep Learning', 'Advanced topics in deep learning with a focus on computer vision.', 6, 1, 'Fall 2025', 70, 0),
('AAI2002', 'AAI2002', 'ITP: Cross Domain Prototyping', 'Integrative team project focused on prototyping solutions.', 6, 4, 'Spring 2026', 80, 0),
('AAI3008', 'AAI3008', 'Large Language Models', 'Study of large language models (LLMs) and their applications.', 6, 1, 'Spring 2026', 70, 0),
('AAI2006', 'AAI2006', 'Industry Certification Module', 'Preparation for an industry certification in AI or data science.', 6, 4, 'Spring 2026', 80, 0),
('AAI2114', 'AAI2114', 'ITP: Execution and Delivery', 'Integrative team project focused on product delivery.', 6, 4, 'Spring 2026', 80, 0),
('AAI4001', 'AAI4001', 'Capstone Project', 'A final year project for Applied AI students.', 5, 4, 'Fall 2025', 100, 0),
('AAI4002B', 'AAI4002B', 'Integrated Work Study Programme (Work Attachment)', 'Work placement for Applied AI students.', 10, 4, 'Fall 2025', 100, 0),
('CSC1103', 'CSC1103', 'Programming Methodology', 'A deeper dive into programming methodologies and problem-solving.', 6, 1, 'Fall 2025', 100, 0),
('CSC1104', 'CSC1104', 'Computer Organisation & Architecture', 'Fundamentals of computer hardware, architecture, and organization.', 6, 2, 'Fall 2025', 100, 0),
('CSC1108', 'CSC1108', 'Data Structures and Algorithms', 'Core module on data structures and algorithms for computing science.', 6, 1, 'Spring 2026', 100, 0),
('CSC1109', 'CSC1109', 'Object Oriented Programming', 'Principles of OOP for computing science students.', 6, 1, 'Spring 2026', 100, 0),
('CSC1106', 'CSC1106', 'Web Programming', 'Development of client-side and server-side web applications.', 6, 1, 'Fall 2025', 90, 0),
('CSC1107', 'CSC1107', 'Operating Systems', 'Study of the principles and design of modern operating systems.', 6, 2, 'Fall 2025', 90, 0),
('CSC2101', 'CSC2101', 'Professional Software Development and Team Project 1', 'Team-based project to learn professional software development practices.', 6, 4, 'Fall 2025', 90, 0),
('CSC3104', 'CSC3104', 'Cloud and Distributed Computing', 'Principles of distributed systems and cloud computing platforms.', 6, 2, 'Fall 2025', 80, 0),
('CSC2102', 'CSC2102', 'Professional Software Development and Team Project 2', 'Continuation of the team-based project.', 6, 4, 'Spring 2026', 90, 0),
('CSC2106', 'CSC2106', 'Internet of Things: Protocols and Networks', 'A study of the network protocols and architectures used in IoT systems.', 6, 2, 'Spring 2026', 70, 0),
('CSC3105', 'CSC3105', 'Data Analytics', 'Techniques for analyzing and interpreting large datasets.', 6, 1, 'Spring 2026', 80, 0),
('CSC3107', 'CSC3107', 'Information Visualisation', 'Principles and techniques for creating effective visualizations of complex data.', 6, 1, 'Fall 2025', 70, 0),
('CSC3109', 'CSC3109', 'Machine Learning', 'Introduction to the concepts and algorithms of machine learning.', 6, 1, 'Fall 2025', 80, 0),
('CSC3108', 'CSC3108', 'Special Topics in Emerging Technologies', 'Explores advanced and emerging topics in computing.', 3, 1, 'Fall 2025', 50, 0),
('CSC3101', 'CSC3101', 'Capstone Project', 'A final year project for Computing Science students.', 5, 4, 'Fall 2025', 100, 0),
('CSC3102B', 'CSC3102B', 'Integrated Work Study Programme (Work Attachment)', 'Work placement for Computing Science students.', 10, 4, 'Fall 2025', 100, 0),
('BAC1001', 'BAC1001', 'Introduction to Fintech (Integrated Workplace Learning 1)', 'An overview of financial technologies and their applications.', 6, 4, 'Fall 2025', 80, 0),
('BAC1002', 'BAC1002', 'Industry Certification', 'Preparation for a professional industry certification in finance or tech.', 6, 4, 'Fall 2025', 80, 0),
('BAC2004', 'BAC2004', 'Foundations of Fintech Finance', 'Core principles of finance as applied to financial technology.', 6, 4, 'Fall 2025', 80, 0),
('BAC2005', 'BAC2005', 'Fintech Investment and Risk Management', 'Managing investments and risk using fintech solutions.', 6, 4, 'Fall 2025', 70, 0),
('BAC2001', 'BAC2001', 'Software Requirements Engineering and Design', 'Principles of Requirements Engineering and Software Design.', 6, 1, 'Spring 2026', 70, 0),
('BAC2002', 'BAC2002', 'Blockchain and Cryptocurrency', 'Fundamentals of blockchain technology and cryptocurrencies.', 6, 1, 'Spring 2026', 70, 0),
('BAC3001', 'BAC3001', 'Business Valuation and Analysis', 'Techniques for valuing businesses and analyzing financial performance.', 6, 4, 'Spring 2026', 60, 0),
('BAC2003', 'BAC2003', 'Fintech Projects (Integrated Workplace Learning 2)', 'A project-based module on fintech solutions.', 6, 4, 'Fall 2025', 70, 0),
('BAC3002', 'BAC3002', 'Fintech: Advanced Topics', 'Explores advanced and emerging topics in financial technology.', 6, 1, 'Fall 2025', 60, 0),
('BAC3005', 'BAC3005', 'Project Management and Workplace Ethics', 'Covers project management methodologies and ethical conduct.', 3, 4, 'Fall 2025', 80, 0),
('BAC3003B', 'BAC3003B', 'Integrated Work Study Programme (Work Attachment)', 'Work placement for Applied Computing students.', 10, 4, 'Fall 2025', 80, 0),
('BAC3004', 'BAC3004', 'Capstone Project', 'A final year project for Applied Computing students.', 5, 4, 'Fall 2025', 80, 0),
('CSD1101', 'CSD1101', 'Computer Environment', 'Introduction to the computing environment for game development.', 6, 2, 'Fall 2025', 60, 0),
('CSD1121', 'CSD1121', 'High-Level Programming 1', 'Foundational programming in C++ for real-time simulation.', 6, 1, 'Fall 2025', 60, 0),
('CSD1241', 'CSD1241', 'Linear Algebra and Geometry', 'Mathematics for computer graphics and physics.', 6, 3, 'Fall 2025', 60, 0),
('CSD1401', 'CSD1401', 'Software Engineering Project 1', 'First project in a series on software engineering.', 6, 4, 'Fall 2025', 60, 0),
('CSD1130', 'CSD1130', 'Game Implementation Techniques', 'Techniques for implementing core game logic and systems.', 5, 1, 'Spring 2026', 60, 0),
('CSD1171', 'CSD1171', 'High-Level Programming 2', 'Advanced C++ programming concepts.', 6, 1, 'Spring 2026', 60, 0),
('CSD1251', 'CSD1251', 'Calculus and Analytic Geometry 1', 'Calculus for simulation and game physics.', 6, 3, 'Spring 2026', 60, 0),
('CSD1451', 'CSD1451', 'Software Engineering Project 2', 'Second project in a series on software engineering.', 6, 4, 'Spring 2026', 60, 0),
('CSD2101', 'CSD2101', 'Introduction to Computer Graphics', 'Fundamentals of 2D and 3D computer graphics.', 6, 1, 'Fall 2025', 60, 0),
('CSD2126', 'CSD2126', 'Modern C++ Design Patterns', 'Applying design patterns in C++ for game development.', 6, 1, 'Fall 2025', 60, 0),
('CSD2182', 'CSD2182', 'Operating Systems', 'Principles of operating systems for RTIS students.', 6, 2, 'Fall 2025', 60, 0),
('CSD2183', 'CSD2183', 'Data Structures', 'Data structures optimized for real-time performance.', 6, 1, 'Fall 2025', 60, 0),
('CSD2201', 'CSD2201', 'Calculus and Analytic Geometry 2', 'Advanced calculus for simulation.', 6, 3, 'Fall 2LAST 2025', 60, 0),
('CSD2401', 'CSD2401', 'Software Engineering Project 3', 'Third project in a series on software engineering.', 6, 4, 'Fall 2025', 60, 0),
('CSD2151', 'CSD2151', 'Introduction to Real-Time Rendering', 'Techniques for rendering graphics in real-time.', 6, 1, 'Spring 2026', 60, 0),
('CSD2161', 'CSD2161', 'Computer Networks', 'Network programming for multiplayer games and simulations.', 6, 2, 'Spring 2026', 60, 0),
('CSD2259', 'CSD2259', 'Discrete Mathematics', 'Discrete math for computer science.', 6, 3, 'Spring 2026', 60, 0),
('CSD2451', 'CSD2451', 'Software Engineering Project 4', 'Fourth project in a series on software engineering.', 6, 4, 'Spring 2026', 60, 0),
('CSD3121', 'CSD3121', 'Developing Immersive Applications', 'Creating applications for VR and AR.', 6, 1, 'Spring 2026', 60, 0),
('CSD2251', 'CSD2251', 'Linear Algebra', 'Advanced linear algebra for graphics and physics.', 6, 3, 'Fall 2025', 60, 0),
('CSD2301', 'CSD2301', 'Motion Dynamics and Lab', 'Physics-based motion and dynamics simulation.', 6, 3, 'Fall 2025', 60, 0),
('CSD3151', 'CSD3151', 'Spatial Data Structures', 'Data structures for managing 3D spatial data (e.g., Octrees).', 6, 1, 'Fall 2025', 60, 0),
('CSD3183', 'CSD3183', 'Artificial Intelligence for Games', 'AI techniques for game characters and systems.', 6, 1, 'Fall 2025', 60, 0),
('CSD3116', 'CSD3116', 'Low-Level Programming', 'Low-level programming and optimization.', 6, 1, 'Fall 2025', 60, 0),
('CSD3131', 'CSD3131', 'Algorithm Analysis', 'Analysis of algorithm performance and complexity.', 6, 1, 'Fall 2025', 60, 0),
('CSD3241', 'CSD3241', 'Probability and Statistics', 'Statistics for simulation and data analysis.', 6, 3, 'Fall 2025', 60, 0),
('CSD3401', 'CSD3401', 'Software Engineering Project 5', 'Fifth project in a series on software engineering.', 6, 4, 'Fall 2025', 60, 0),
('CSD2171', 'CSD2171', 'Programming Massively Parallel Processors', 'CUDA/GPU programming for high performance.', 6, 1, 'Spring 2026', 60, 0),
('CSD3156', 'CSD3156', 'Mobile and Cloud Computing', 'Developing for mobile and cloud platforms.', 6, 1, 'Spring 2026', 60, 0),
('CSD3186', 'CSD3186', 'Machine Learning', 'Introduction to machine learning for RTIS.', 6, 1, 'Spring 2026', 60, 0),
('CSD3451', 'CSD3451', 'Software Engineering Project 6', 'Final project in a series on software engineering.', 6, 4, 'Spring 2026', 60, 0),
('CSD4401', 'CSD4401', 'Capstone Project', 'A final year project for RTIS students.', 3, 4, 'Fall 2025', 60, 0),
('CSD4902B', 'CSD4902B', 'Integrated Work Study Programme (Work Attachment)', 'Work placement for RTIS students.', 10, 4, 'Fall 2025', 60, 0),
('ICT1013', 'ICT1013', 'Computer Networks', 'Fundamentals of computer networking, TCP/IP, and security (IS focus).', 6, 2, 'Spring 2026', 100, 0),
('ICT2217', 'ICT2217', 'Network Security', 'Theory and practices of network attacks and defenses.', 6, 2, 'Fall 2025', 80, 0),
('ICT2212', 'ICT2212', 'Ethical Hacking', 'Principles and techniques of ethical hacking and penetration testing.', 6, 2, 'Fall 2025', 80, 0),
('ICT2213', 'ICT2213', 'Applied Cryptography', 'Modern cryptographic techniques and their application.', 6, 2, 'Spring 2026', 80, 0),
('ICT2214', 'ICT2214', 'Web Security', 'Security vulnerabilities of web applications and defenses.', 6, 2, 'Spring 2026', 80, 0),
('ICT3212', 'ICT3212', 'Operations Security and Incident Management', 'Managing security operations and responding to incidents.', 6, 2, 'Fall 2025', 70, 0),
('ICT3215', 'ICT3215', 'Digital Forensics', 'Investigating cybercrimes and analyzing digital evidence.', 6, 2, 'Fall 2025', 70, 0),
('ICT3214', 'ICT3214', 'Security Analytics', 'Using data analytics to detect and investigate security threats.', 6, 1, 'Fall 2025', 70, 0),
('ICT3213', 'ICT3213', 'Malware Analysis and Defence', 'Techniques for analyzing malicious software.', 6, 2, 'Spring 2026', 70, 0),
('ICT3218', 'ICT3218', 'Security Governance, Risk Management and Compliance', 'Frameworks for managing security, risk, and compliance.', 6, 4, 'Spring 2026', 80, 0),
('ICT3216', 'ICT3216', 'Special Topics in Security', 'Explores advanced and emerging topics in information security.', 6, 2, 'Spring 2026', 60, 0),
('CSD2511', 'CSD2511', 'Introduction to Game Design', 'Fundamentals of game design, mechanics, and documentation.', 6, 4, 'Fall 2025', 60, 0),
('CSD2513', 'CSD2513', 'System Design Methods', 'Methods for designing complex game systems.', 6, 4, 'Spring 2026', 60, 0),
('CSD2541', 'CSD2541', 'Level Design', 'Principles and practices of designing game levels.', 6, 4, 'Fall 2025', 60, 0),
('CSD2702', 'CSD2702', 'Introduction to Psychology', 'Understanding player psychology and motivation.', 6, 4, 'Fall 2025', 60, 0),
('CSD3516', 'CSD3516', 'Technical Design Methods', 'Technical aspects of game and system design.', 6, 1, 'Fall 2025', 60, 0),
('CSD3126', 'CSD3126', 'User Interface and User Experience Design', 'Designing UIs and UX for games and interactive media.', 6, 4, 'Spring 2026', 60, 0);

/* =========================================================
STEP 6: POPULATE PREREQUISITES
=========================================================
*/
INSERT INTO prerequisites (course_id, requires_course_id)
VALUES
-- General Math
('INF1004', 'INF1003'), -- Math 2 requires Math 1
('CSD1251', 'CSD1241'), 
('CSD2201', 'CSD1251'), 

-- Computing Science
('CSC1108', 'CSC1103'), 
('CSC1109', 'CSC1103'), 

-- Software Engineering
('INF1009', 'INF1002'), 
('INF1008', 'INF1002'), 
('ICT1012', 'ICT1011'), 

-- Applied AI
('AAI3001', 'INF2008');

/* =========================================================
STEP 7: POPULATE YOUR ACADEMIC HISTORY (Alex)
=========================================================
*/
-- --- YEAR 1, TRIMESTER 1 (Completed) ---
INSERT INTO enrollments (student_id, course_id, semester, final_grade, status)
VALUES
(1001, 'ICT1011', 'Y1T1', 'A', 'Completed'),
(1001, 'INF1001', 'Y1T1', 'A-', 'Completed'),
(1001, 'INF1002', 'Y1T1', 'A', 'Completed'),
(1001, 'INF1003', 'Y1T1', 'A-', 'Completed');

-- --- YEAR 1, TRIMESTER 2 (Completed) ---
INSERT INTO enrollments (student_id, course_id, semester, final_grade, status)
VALUES
(1001, 'ICT1012', 'Y1T2', 'B+', 'Completed'),
(1001, 'INF1004', 'Y1T2', 'A', 'Completed'),
(1001, 'INF1005', 'Y1T2', 'A-', 'Completed'),
(1001, 'INF1009', 'Y1T2', 'B+', 'Completed');

-- --- YEAR 1, TRIMESTER 3 (Completed) ---
INSERT INTO enrollments (student_id, course_id, semester, final_grade, status)
VALUES
(1001, 'INF1006', 'Y1T3', 'A-', 'Completed'),
(1001, 'INF1007', 'Y1T3', 'A', 'Completed'),
(1001, 'INF1008', 'Y1T3', 'A', 'Completed');

-- --- YEAR 2, TRIMESTER 1 (Currently Enrolled) ---
INSERT INTO enrollments (student_id, course_id, semester, final_grade, status)
VALUES
(1001, 'INF2001', 'Y2T1', NULL, 'Enrolled'),
(1001, 'INF2002', 'Y2T1', NULL, 'Enrolled'),
(1001, 'INF2003', 'Y2T1', NULL, 'Enrolled'), 
(1001, 'INF2004', 'Y2T1', NULL, 'Enrolled');

/* =========================================================
STEP 8: UPDATE ENROLLMENT COUNTS
=========================================================
*/
UPDATE courses SET current_enrollment = COALESCE(current_enrollment, 0) + 1 WHERE course_id IN ('INF2001', 'INF2002', 'INF2003', 'INF2004');

/* =========================================================
STEP 9: RESET SAFE UPDATES
=========================================================
*/
SET SQL_SAFE_UPDATES = 1;

/* =========================================================
END OF COMPLETE SCRIPT
=========================================================
*/

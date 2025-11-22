import pymongo
from pymongo import MongoClient
from datetime import datetime

# 1. Configuration
MONGO_URI = "mongodb+srv://inf2003-admin:wRy7zbLFw7jjRGEt@cluster0.spxkjcp.mongodb.net/ucms_db?appName=Cluster0"
DB_NAME = 'ucms_db'

# 2. Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def seed_collection(collection_name, data):
    """Helper to clear and repopulate a collection"""
    collection = db[collection_name]
    collection.delete_many({}) # Clear existing data
    if data:
        collection.insert_many(data)
    print(f"✅ Populated '{collection_name}' with {len(data)} documents.")

# ==========================================
# 3. Data Definitions (Parsed from SQL Dump)
# ==========================================

# --- Table: users ---
users_data = [
    {"user_id": 1, "university_id": "I-001", "email": "admin@ucms.edu", "password_hash": "hashed_pass_1", "first_name": "Admin", "last_name": "Boy", "role": "admin", "is_active": True, "date_joined": datetime(2025, 11, 11, 12, 47, 3)},
    {"user_id": 2, "university_id": "I-002", "email": "instructor1@ucms.edu", "password_hash": "hashed_pass_2", "first_name": "Ada", "last_name": "Lovelace", "role": "instructor", "is_active": True, "date_joined": datetime(2025, 11, 11, 12, 47, 3)},
    {"user_id": 3, "university_id": "I-003", "email": "instructor3@ucms.edu", "password_hash": "hashed_pass_3", "first_name": "Grace", "last_name": "Hopper", "role": "instructor", "is_active": True, "date_joined": datetime(2025, 11, 11, 12, 47, 3)},
    {"user_id": 4, "university_id": "I-004", "email": "instructor4@ucms.edu", "password_hash": "hashed_pass_4", "first_name": "Siti", "last_name": "Nurhaliza", "role": "instructor", "is_active": True, "date_joined": datetime(2025, 11, 11, 12, 47, 3)},
    {"user_id": 1001, "university_id": "S2401001A", "email": "alex.student@ucms.edu", "password_hash": "hashed_pass_s1", "first_name": "Alex", "last_name": "Cross", "role": "student", "is_active": True, "date_joined": datetime(2024, 8, 20, 10, 0, 0)},
    {"user_id": 1009, "university_id": "2403052", "email": "tykcuber@gmail.com", "password_hash": "default_password", "first_name": "Tan Ye", "last_name": "Ye Kai", "role": "student", "is_active": True, "date_joined": datetime(2025, 11, 17, 17, 22, 39)}
]

# --- Table: instructors ---
instructors_data = [
    {"instructor_id": 1, "department_code": "CS", "office_location": "SIT@Dover, C-01-01", "office_hours": "Mon/Wed 10-12", "title": "Professor"},
    {"instructor_id": 2, "department_code": "INF", "office_location": "SIT@Dover, D-05-01", "office_hours": "Mon 10:00-12:00", "title": "Associate Professor"},
    {"instructor_id": 3, "department_code": "BUS", "office_location": "SIT@Dover, B-02-05", "office_hours": "Wed 14:00-16:00", "title": "Lecturer"},
    {"instructor_id": 4, "department_code": "GEN", "office_location": "SIT@Dover, A-04-01", "office_hours": "Fri 09:00-11:00", "title": "Lecturer"}
]

# --- Table: students ---
students_data = [
    {"student_id": 1001, "enrollment_year": 2024, "major": "BEng (Hons) ICT (Software Engineering)", "expected_graduation": "2028", "gpa": 4.00, "current_standing": "Year 2"},
    {"student_id": 1009, "enrollment_year": 2025, "major": "ICT(SE)", "expected_graduation": None, "gpa": 0.00, "current_standing": "Year 1"}
]

# --- Table: prerequisites ---
prerequisites_data = [
    {"course_id": "CSC1108", "requires_course_id": "CSC1103"},
    {"course_id": "CSC1109", "requires_course_id": "CSC1103"},
    {"course_id": "CSD1251", "requires_course_id": "CSD1241"},
    {"course_id": "CSD2201", "requires_course_id": "CSD1251"},
    {"course_id": "ICT1012", "requires_course_id": "ICT1011"},
    {"course_id": "INF1008", "requires_course_id": "INF1002"},
    {"course_id": "INF1009", "requires_course_id": "INF1002"},
    {"course_id": "INF1004", "requires_course_id": "INF1003"},
    {"course_id": "AAI3001", "requires_course_id": "INF2008"}
]

# --- Table: enrollments ---
enrollments_data = [
    {"student_id": 1001, "course_id": "AAI1001", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 15, 15, 36, 37)},
    {"student_id": 1001, "course_id": "AAI2002", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 13, 6, 58, 49)},
    {"student_id": 1001, "course_id": "AAI2006", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 13, 6, 58, 55)},
    {"student_id": 1001, "course_id": "AAI2007", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 13, 6, 58, 59)},
    {"student_id": 1001, "course_id": "AAI2114", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 14, 4, 35, 17)},
    {"student_id": 1001, "course_id": "AAI3008", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 15, 15, 3, 45)},
    {"student_id": 1001, "course_id": "AAI4002B", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 17, 17, 22, 2)},
    {"student_id": 1001, "course_id": "ICT1011", "semester": "Y1T1", "status": "Completed", "final_grade": "A", "enrolled_at": datetime(2025, 11, 11, 12, 47, 4)},
    {"student_id": 1001, "course_id": "ICT1012", "semester": "Y1T2", "status": "Completed", "final_grade": "B+", "enrolled_at": datetime(2025, 11, 11, 12, 47, 5)},
    {"student_id": 1001, "course_id": "INF1001", "semester": "Y1T1", "status": "Completed", "final_grade": "A-", "enrolled_at": datetime(2025, 11, 11, 12, 47, 4)},
    {"student_id": 1001, "course_id": "INF1002", "semester": "Y1T1", "status": "Completed", "final_grade": "A", "enrolled_at": datetime(2025, 11, 11, 12, 47, 4)},
    {"student_id": 1001, "course_id": "INF1003", "semester": "Y1T1", "status": "Completed", "final_grade": "A-", "enrolled_at": datetime(2025, 11, 11, 12, 47, 4)},
    {"student_id": 1001, "course_id": "INF1004", "semester": "Y1T2", "status": "Completed", "final_grade": "A", "enrolled_at": datetime(2025, 11, 11, 12, 47, 5)},
    {"student_id": 1001, "course_id": "INF1005", "semester": "Y1T2", "status": "Completed", "final_grade": "A-", "enrolled_at": datetime(2025, 11, 11, 12, 47, 5)},
    {"student_id": 1001, "course_id": "INF1006", "semester": "Y1T3", "status": "Completed", "final_grade": "A-", "enrolled_at": datetime(2025, 11, 11, 12, 47, 5)},
    {"student_id": 1001, "course_id": "INF1007", "semester": "Y1T3", "status": "Completed", "final_grade": "A", "enrolled_at": datetime(2025, 11, 11, 12, 47, 5)},
    {"student_id": 1001, "course_id": "INF1008", "semester": "Y1T3", "status": "Completed", "final_grade": "A", "enrolled_at": datetime(2025, 11, 11, 12, 47, 5)},
    {"student_id": 1001, "course_id": "INF1009", "semester": "Y1T2", "status": "Completed", "final_grade": "B+", "enrolled_at": datetime(2025, 11, 11, 12, 47, 5)},
    {"student_id": 1001, "course_id": "INF2008", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 17, 17, 14, 39)},
    {"student_id": 1009, "course_id": "AAI1001", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 17, 17, 22, 52)},
    {"student_id": 1009, "course_id": "AAI2002", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 17, 17, 22, 55)},
    {"student_id": 1009, "course_id": "AAI2006", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 17, 17, 22, 59)},
    {"student_id": 1009, "course_id": "BAC2001", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 17, 17, 23, 16)},
    {"student_id": 1009, "course_id": "CSC1104", "semester": "Fall 2025", "status": "Enrolled", "enrolled_at": datetime(2025, 11, 17, 17, 24, 33)}
]

# --- Table: courses ---
# I have parsed all the courses from your dump file.
courses_data = [
    {'course_id': 'AAI1001', 'course_code': 'AAI1001', 'course_name': 'Data Engineering and Visualization', 'description': 'Techniques for collecting, cleaning, and visualizing large datasets.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 2, 'instructor_id': 1},
    {'course_id': 'AAI2002', 'course_code': 'AAI2002', 'course_name': 'ITP: Cross Domain Prototyping', 'description': 'Integrative team project focused on prototyping solutions.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 80, 'current_enrollment': 2, 'instructor_id': 4},
    {'course_id': 'AAI2006', 'course_code': 'AAI2006', 'course_name': 'Industry Certification Module', 'description': 'Preparation for an industry certification in AI or data science.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 80, 'current_enrollment': 2, 'instructor_id': 4},
    {'course_id': 'AAI2007', 'course_code': 'AAI2007', 'course_name': 'Artificial Intelligence in Business and Society', 'description': 'Examines the impact of AI on business and societal issues.', 'credits': 3, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 1, 'instructor_id': 4},
    {'course_id': 'AAI2114', 'course_code': 'AAI2114', 'course_name': 'ITP: Execution and Delivery', 'description': 'Integrative team project focused on product delivery.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 80, 'current_enrollment': 1, 'instructor_id': 4},
    {'course_id': 'AAI3001', 'course_code': 'AAI3001', 'course_name': 'Computer Vision and Deep Learning', 'description': 'Advanced topics in deep learning with a focus on computer vision.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'AAI3008', 'course_code': 'AAI3008', 'course_name': 'Large Language Models', 'description': 'Study of large language models (LLMs) and their applications.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 70, 'current_enrollment': 1, 'instructor_id': 1},
    {'course_id': 'AAI4001', 'course_code': 'AAI4001', 'course_name': 'Capstone Project', 'description': 'A final year project for Applied AI students.', 'credits': 5, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'AAI4002B', 'course_code': 'AAI4002B', 'course_name': 'Integrated Work Study Programme (Work Attachment)', 'description': 'Work placement for Applied AI students.', 'credits': 10, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 1, 'instructor_id': 4},
    {'course_id': 'BAC1001', 'course_code': 'BAC1001', 'course_name': 'Introduction to Fintech (Integrated Workplace Learning 1)', 'description': 'An overview of financial technologies and their applications.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'BAC1002', 'course_code': 'BAC1002', 'course_name': 'Industry Certification', 'description': 'Preparation for a professional industry certification in finance or tech.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'BAC2001', 'course_code': 'BAC2001', 'course_name': 'Software Requirements Engineering and Design', 'description': 'Principles of Requirements Engineering and Software Design.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 70, 'current_enrollment': 1, 'instructor_id': 1},
    {'course_id': 'BAC2002', 'course_code': 'BAC2002', 'course_name': 'Blockchain and Cryptocurrency', 'description': 'Fundamentals of blockchain technology and cryptocurrencies.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'BAC2003', 'course_code': 'BAC2003', 'course_name': 'Fintech Projects (Integrated Workplace Learning 2)', 'description': 'A project-based module on fintech solutions.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'BAC2004', 'course_code': 'BAC2004', 'course_name': 'Foundations of Fintech Finance', 'description': 'Core principles of finance as applied to financial technology.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'BAC2005', 'course_code': 'BAC2005', 'course_name': 'Fintech Investment and Risk Management', 'description': 'Managing investments and risk using fintech solutions.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'BAC3001', 'course_code': 'BAC3001', 'course_name': 'Business Valuation and Analysis', 'description': 'Techniques for valuing businesses and analyzing financial performance.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'BAC3002', 'course_code': 'BAC3002', 'course_name': 'Fintech: Advanced Topics', 'description': 'Explores advanced and emerging topics in financial technology.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'BAC3003B', 'course_code': 'BAC3003B', 'course_name': 'Integrated Work Study Programme (Work Attachment)', 'description': 'Work placement for Applied Computing students.', 'credits': 10, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'BAC3004', 'course_code': 'BAC3004', 'course_name': 'Capstone Project', 'description': 'A final year project for Applied Computing students.', 'credits': 5, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'BAC3005', 'course_code': 'BAC3005', 'course_name': 'Project Management and Workplace Ethics', 'description': 'Covers project management methodologies and ethical conduct.', 'credits': 3, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CS101', 'course_code': 'CS101', 'course_name': 'Intro to comp sc', 'description': 'edfa', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 30, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSC1103', 'course_code': 'CSC1103', 'course_name': 'Programming Methodology', 'description': 'A deeper dive into programming methodologies and problem-solving.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSC1104', 'course_code': 'CSC1104', 'course_name': 'Computer Organisation & Architecture', 'description': 'Fundamentals of computer hardware, architecture, and organization.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 1, 'instructor_id': 2},
    {'course_id': 'CSC1106', 'course_code': 'CSC1106', 'course_name': 'Web Programming', 'description': 'Development of client-side and server-side web applications.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 90, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSC1107', 'course_code': 'CSC1107', 'course_name': 'Operating Systems', 'description': 'Study of the principles and design of modern operating systems.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 90, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'CSC1108', 'course_code': 'CSC1108', 'course_name': 'Data Structures and Algorithms', 'description': 'Core module on data structures and algorithms for computing science.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSC1109', 'course_code': 'CSC1109', 'course_name': 'Object Oriented Programming', 'description': 'Principles of OOP for computing science students.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSC2101', 'course_code': 'CSC2101', 'course_name': 'Professional Software Development and Team Project 1', 'description': 'Team-based project to learn professional software development practices.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 90, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSC2102', 'course_code': 'CSC2102', 'course_name': 'Professional Software Development and Team Project 2', 'description': 'Continuation of the team-based project.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 90, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSC2106', 'course_code': 'CSC2106', 'course_name': 'Internet of Things: Protocols and Networks', 'description': 'A study of the network protocols and architectures used in IoT systems.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'CSC3101', 'course_code': 'CSC3101', 'course_name': 'Capstone Project', 'description': 'A final year project for Computing Science students.', 'credits': 5, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSC3102B', 'course_code': 'CSC3102B', 'course_name': 'Integrated Work Study Programme (Work Attachment)', 'description': 'Work placement for Computing Science students.', 'credits': 10, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSC3104', 'course_code': 'CSC3104', 'course_name': 'Cloud and Distributed Computing', 'description': 'Principles of distributed systems and cloud computing platforms.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'CSC3105', 'course_code': 'CSC3105', 'course_name': 'Data Analytics', 'description': 'Techniques for analyzing and interpreting large datasets.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSC3107', 'course_code': 'CSC3107', 'course_name': 'Information Visualisation', 'description': 'Principles and techniques for creating effective visualizations of complex data.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSC3108', 'course_code': 'CSC3108', 'course_name': 'Special Topics in Emerging Technologies', 'description': 'Explores advanced and emerging topics in computing.', 'credits': 3, 'academic_term': 'Fall 2025', 'max_capacity': 50, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSC3109', 'course_code': 'CSC3109', 'course_name': 'Machine Learning', 'description': 'Introduction to the concepts and algorithms of machine learning.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD1101', 'course_code': 'CSD1101', 'course_name': 'Computer Environment', 'description': 'Introduction to the computing environment for game development.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'CSD1121', 'course_code': 'CSD1121', 'course_name': 'High-Level Programming 1', 'description': 'Foundational programming in C++ for real-time simulation.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD1130', 'course_code': 'CSD1130', 'course_name': 'Game Implementation Techniques', 'description': 'Techniques for implementing core game logic and systems.', 'credits': 5, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD1171', 'course_code': 'CSD1171', 'course_name': 'High-Level Programming 2', 'description': 'Advanced C++ programming concepts.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD1241', 'course_code': 'CSD1241', 'course_name': 'Linear Algebra and Geometry', 'description': 'Mathematics for computer graphics and physics.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 3},
    {'course_id': 'CSD1251', 'course_code': 'CSD1251', 'course_name': 'Calculus and Analytic Geometry 1', 'description': 'Calculus for simulation and game physics.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 3},
    {'course_id': 'CSD1401', 'course_code': 'CSD1401', 'course_name': 'Software Engineering Project 1', 'description': 'First project in a series on software engineering.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD1451', 'course_code': 'CSD1451', 'course_name': 'Software Engineering Project 2', 'description': 'Second project in a series on software engineering.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD2101', 'course_code': 'CSD2101', 'course_name': 'Introduction to Computer Graphics', 'description': 'Fundamentals of 2D and 3D computer graphics.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD2126', 'course_code': 'CSD2126', 'course_name': 'Modern C++ Design Patterns', 'description': 'Applying design patterns in C++ for game development.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD2151', 'course_code': 'CSD2151', 'course_name': 'Introduction to Real-Time Rendering', 'description': 'Techniques for rendering graphics in real-time.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD2161', 'course_code': 'CSD2161', 'course_name': 'Computer Networks', 'description': 'Network programming for multiplayer games and simulations.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'CSD2171', 'course_code': 'CSD2171', 'course_name': 'Programming Massively Parallel Processors', 'description': 'CUDA/GPU programming for high performance.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD2182', 'course_code': 'CSD2182', 'course_name': 'Operating Systems', 'description': 'Principles of operating systems for RTIS students.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'CSD2183', 'course_code': 'CSD2183', 'course_name': 'Data Structures', 'description': 'Data structures optimized for real-time performance.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD2201', 'course_code': 'CSD2201', 'course_name': 'Calculus and Analytic Geometry 2', 'description': 'Advanced calculus for simulation.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 3},
    {'course_id': 'CSD2251', 'course_code': 'CSD2251', 'course_name': 'Linear Algebra', 'description': 'Advanced linear algebra for graphics and physics.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 3},
    {'course_id': 'CSD2259', 'course_code': 'CSD2259', 'course_name': 'Discrete Mathematics', 'description': 'Discrete math for computer science.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 3},
    {'course_id': 'CSD2301', 'course_code': 'CSD2301', 'course_name': 'Motion Dynamics and Lab', 'description': 'Physics-based motion and dynamics simulation.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 3},
    {'course_id': 'CSD2401', 'course_code': 'CSD2401', 'course_name': 'Software Engineering Project 3', 'description': 'Third project in a series on software engineering.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD2451', 'course_code': 'CSD2451', 'course_name': 'Software Engineering Project 4', 'description': 'Fourth project in a series on software engineering.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD2511', 'course_code': 'CSD2511', 'course_name': 'Introduction to Game Design', 'description': 'Fundamentals of game design, mechanics, and documentation.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD2513', 'course_code': 'CSD2513', 'course_name': 'System Design Methods', 'description': 'Methods for designing complex game systems.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD2541', 'course_code': 'CSD2541', 'course_name': 'Level Design', 'description': 'Principles and practices of designing game levels.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD2702', 'course_code': 'CSD2702', 'course_name': 'Introduction to Psychology', 'description': 'Understanding player psychology and motivation.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD3116', 'course_code': 'CSD3116', 'course_name': 'Low-Level Programming', 'description': 'Low-level programming and optimization.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD3121', 'course_code': 'CSD3121', 'course_name': 'Developing Immersive Applications', 'description': 'Creating applications for VR and AR.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD3126', 'course_code': 'CSD3126', 'course_name': 'User Interface and User Experience Design', 'description': 'Designing UIs and UX for games and interactive media.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD3131', 'course_code': 'CSD3131', 'course_name': 'Algorithm Analysis', 'description': 'Analysis of algorithm performance and complexity.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD3151', 'course_code': 'CSD3151', 'course_name': 'Spatial Data Structures', 'description': 'Data structures for managing 3D spatial data (e.g., Octrees).', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD3156', 'course_code': 'CSD3156', 'course_name': 'Mobile and Cloud Computing', 'description': 'Developing for mobile and cloud platforms.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD3183', 'course_code': 'CSD3183', 'course_name': 'Artificial Intelligence for Games', 'description': 'AI techniques for game characters and systems.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD3186', 'course_code': 'CSD3186', 'course_name': 'Machine Learning', 'description': 'Introduction to machine learning for RTIS.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD3241', 'course_code': 'CSD3241', 'course_name': 'Probability and Statistics', 'description': 'Statistics for simulation and data analysis.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 3},
    {'course_id': 'CSD3401', 'course_code': 'CSD3401', 'course_name': 'Software Engineering Project 5', 'description': 'Fifth project in a series on software engineering.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD3451', 'course_code': 'CSD3451', 'course_name': 'Software Engineering Project 6', 'description': 'Final project in a series on software engineering.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD3516', 'course_code': 'CSD3516', 'course_name': 'Technical Design Methods', 'description': 'Technical aspects of game and system design.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'CSD4401', 'course_code': 'CSD4401', 'course_name': 'Capstone Project', 'description': 'A final year project for RTIS students.', 'credits': 3, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'CSD4902B', 'course_code': 'CSD4902B', 'course_name': 'Integrated Work Study Programme (Work Attachment)', 'description': 'Work placement for RTIS students.', 'credits': 10, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'ICT1011', 'course_code': 'ICT1011', 'course_name': 'Computer Organization & Architecture', 'description': 'Fundamentals of computer hardware, architecture, and organization.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT1012', 'course_code': 'ICT1012', 'course_name': 'Operating Systems', 'description': 'Principles and design of modern operating systems, including process and memory management.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT1013', 'course_code': 'ICT1013', 'course_name': 'Computer Networks', 'description': 'Fundamentals of computer networking, TCP/IP, and security (IS focus).', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT2112', 'course_code': 'ICT2112', 'course_name': 'Software Design', 'description': 'Covers software design patterns, principles, and architectures for building scalable systems.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'ICT2113', 'course_code': 'ICT2113', 'course_name': 'Software Modelling and Analysis', 'description': 'Techniques for modeling and analyzing software systems using UML and other notations.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'ICT2114', 'course_code': 'ICT2114', 'course_name': 'Integrative Team Project', 'description': 'A project module where students work in teams to develop a software solution.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'ICT2212', 'course_code': 'ICT2212', 'course_name': 'Ethical Hacking', 'description': 'Principles and techniques of ethical hacking and penetration testing.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT2213', 'course_code': 'ICT2213', 'course_name': 'Applied Cryptography', 'description': 'Modern cryptographic techniques and their application.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT2214', 'course_code': 'ICT2214', 'course_name': 'Web Security', 'description': 'Security vulnerabilities of web applications and defenses.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT2215', 'course_code': 'ICT2215', 'course_name': 'Mobile Security', 'description': 'Covers security challenges and defenses for mobile operating systems and applications.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT2216', 'course_code': 'ICT2216', 'course_name': 'Secure Software Development', 'description': 'Teaches principles and practices for building secure and robust software.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'ICT2217', 'course_code': 'ICT2217', 'course_name': 'Network Security', 'description': 'Theory and practices of network attacks and defenses.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT3112', 'course_code': 'ICT3112', 'course_name': 'Software Verification and Validation', 'description': 'Techniques for testing, verifying, and validating software to ensure quality.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'ICT3113', 'course_code': 'ICT3113', 'course_name': 'Performance Testing and Optimisation', 'description': 'Methods for testing and optimizing the performance of software applications.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'ICT3212', 'course_code': 'ICT3212', 'course_name': 'Operations Security and Incident Management', 'description': 'Managing security operations and responding to incidents.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT3213', 'course_code': 'ICT3213', 'course_name': 'Malware Analysis and Defence', 'description': 'Techniques for analyzing malicious software.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT3214', 'course_code': 'ICT3214', 'course_name': 'Security Analytics', 'description': 'Using data analytics to detect and investigate security threats.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'ICT3215', 'course_code': 'ICT3215', 'course_name': 'Digital Forensics', 'description': 'Investigating cybercrimes and analyzing digital evidence.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT3216', 'course_code': 'ICT3216', 'course_name': 'Special Topics in Security', 'description': 'Explores advanced and emerging topics in information security.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'ICT3217', 'course_code': 'ICT3217', 'course_name': 'Integrative Team Project 2', 'description': 'A second, more advanced project module for teams.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'ICT3218', 'course_code': 'ICT3218', 'course_name': 'Security Governance, Risk Management and Compliance', 'description': 'Frameworks for managing security, risk, and compliance.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 80, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'ICT3219', 'course_code': 'ICT3219', 'course_name': 'Industry Certification Module', 'description': 'Preparation for a professional industry certification in cybersecurity or IT.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'ICT4011', 'course_code': 'ICT4011', 'course_name': 'Capstone Project', 'description': 'A year-long final project to design and develop a significant system.', 'credits': 5, 'academic_term': 'Fall 2025', 'max_capacity': 150, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'ICT4012B', 'course_code': 'ICT4012B', 'course_name': 'Integrated Work Study Programme (Work Attachment)', 'description': 'A long-term work placement in a relevant company.', 'credits': 10, 'academic_term': 'Fall 2025', 'max_capacity': 150, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'INF1001', 'course_code': 'INF1001', 'course_name': 'Introduction to Computing', 'description': 'An overview of computing, software, hardware, operating systems, and security.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 150, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'INF1002', 'course_code': 'INF1002', 'course_name': 'Programming Fundamentals', 'description': 'An introduction to foundational programming concepts using a modern language.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 150, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'INF1003', 'course_code': 'INF1003', 'course_name': 'Mathematics 1', 'description': 'Foundational mathematics for computing, including calculus and algebra.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 150, 'current_enrollment': 0, 'instructor_id': 3},
    {'course_id': 'INF1004', 'course_code': 'INF1004', 'course_name': 'Mathematics 2', 'description': 'Further topics in mathematics relevant to computing, including discrete mathematics and statistics.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 150, 'current_enrollment': 0, 'instructor_id': 3},
    {'course_id': 'INF1005', 'course_code': 'INF1005', 'course_name': 'Web Systems & Technologies', 'description': 'Design and development of dynamic web applications, covering front-end and back-end.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 120, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'INF1006', 'course_code': 'INF1006', 'course_name': 'Computer Networks', 'description': 'Fundamentals of computer networking, TCP/IP protocol suite, and network security basics.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'INF1007', 'course_code': 'INF1007', 'course_name': 'Ethics and Professional Conduct', 'description': 'Ethical and professional responsibilities of an ICT professional.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 150, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'INF1008', 'course_code': 'INF1008', 'course_name': 'Data Structures and Algorithms', 'description': 'Core module on the design, analysis, and implementation of data structures and algorithms.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 130, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'INF1009', 'course_code': 'INF1009', 'course_name': 'Object-Oriented Programming', 'description': 'Principles of OOP, including classes, objects, inheritance, and polymorphism.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 130, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'INF1101', 'course_code': 'INF1101', 'course_name': 'Introduction to Computer Systems', 'description': 'A broad overview of computer systems, from hardware to software.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'INF2001', 'course_code': 'INF2001', 'course_name': 'Introduction to Software Engineering', 'description': 'Fundamentals of software engineering principles, practices, and the software development lifecycle.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'INF2002', 'course_code': 'INF2002', 'course_name': 'Human Computer Interaction', 'description': 'Methods and principles for designing, programming, and testing human-centric systems.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 90, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'INF2003', 'course_code': 'INF2003', 'course_name': 'Database Systems', 'description': 'Introduction to database design, implementation, and management. Covers relational models, SQL, and NoSQL.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'INF2004', 'course_code': 'INF2004', 'course_name': 'Embedded Systems Programming', 'description': 'Programming embedded systems, computer architectures, and microcontrollers.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 70, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'INF2005', 'course_code': 'INF2005', 'course_name': 'Cyber Security Fundamentals', 'description': 'Introductory course covering basic principles of cybersecurity.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'INF2006', 'course_code': 'INF2006', 'course_name': 'Cloud Computing and Big Data', 'description': 'Fundamentals of cloud computing architectures and big data technologies.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 90, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'INF2007', 'course_code': 'INF2007', 'course_name': 'Mobile Application Development', 'description': 'Design and development of applications for mobile devices, focusing on Android or iOS.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 90, 'current_enrollment': 0, 'instructor_id': 1},
    {'course_id': 'INF2008', 'course_code': 'INF2008', 'course_name': 'Machine Learning', 'description': 'Introduction to the concepts and algorithms of machine learning.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 100, 'current_enrollment': 1, 'instructor_id': 1},
    {'course_id': 'INF2009', 'course_code': 'INF2009', 'course_name': 'Edge Computing and Analytics', 'description': 'Explores computing and data analytics at the edge of the network.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 60, 'current_enrollment': 0, 'instructor_id': 2},
    {'course_id': 'INF2335', 'course_code': 'INF2335', 'course_name': 'Global Learning in ICT Advances', 'description': 'Explores advanced and emerging topics in the field of ICT.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 50, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'UCM3001', 'course_code': 'UCM3001', 'course_name': 'Change Management', 'description': 'A study of the principles and practices for managing organizational change.', 'credits': 6, 'academic_term': 'Spring 2026', 'max_capacity': 100, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'UCS1001', 'course_code': 'UCS1001', 'course_name': 'Critical Thinking and Communicating', 'description': 'Develops skills in critical analysis, logical reasoning, and effective communication.', 'credits': 4, 'academic_term': 'Spring 2026', 'max_capacity': 200, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'UDC1001', 'course_code': 'UDC1001', 'course_name': 'Digital Competency Essentials', 'description': 'Essential digital literacy skills for the modern university student and professional.', 'credits': 2, 'academic_term': 'Fall 2025', 'max_capacity': 200, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'UDE2222', 'course_code': 'UDE2222', 'course_name': 'Design Innovation', 'description': 'An introduction to design thinking principles and innovation processes.', 'credits': 6, 'academic_term': 'Fall 2025', 'max_capacity': 150, 'current_enrollment': 0, 'instructor_id': 4},
    {'course_id': 'USI2001', 'course_code': 'USI2001', 'course_name': 'Social Innovation Project', 'description': 'A project focused on creating innovative solutions to social problems.', 'credits': 3, 'academic_term': 'Spring 2026', 'max_capacity': 150, 'current_enrollment': 0, 'instructor_id': 4}
]

# 4. Execution
def seed_database():
    print(f"Connecting to MongoDB Cloud...")
    
    seed_collection("users", users_data)
    seed_collection("instructors", instructors_data)
    seed_collection("students", students_data)
    seed_collection("courses", courses_data)
    seed_collection("enrollments", enrollments_data)
    seed_collection("prerequisites", prerequisites_data)
    
    # Create empty collections for consistency (as per your empty SQL tables)
    seed_collection("assignments", [])
    seed_collection("submissions", [])

    print("\n🎉 Database migration complete!")

if __name__ == "__main__":
    seed_database()
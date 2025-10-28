from ..models import db, User, Student, Instructor, Course, Enrollment, Prerequisites
from sqlalchemy import text

# --- Mock Data ---
MOCK_USERS = [
    {"id": 1, "email": "instructor1@ucms.edu", "password_hash": "hashed_pass_1", "first_name": "Alan", "last_name": "Turing", "role": "instructor"},
    {"id": 2, "email": "instructor2@ucms.edu", "password_hash": "hashed_pass_2", "first_name": "Ada", "last_name": "Lovelace", "role": "instructor"},
    {"id": 3, "email": "instructor3@ucms.edu", "password_hash": "hashed_pass_3", "first_name": "Grace", "last_name": "Hopper", "role": "instructor"},
    {"id": 4, "email": "instructor4@ucms.edu", "password_hash": "hashed_pass_4", "first_name": "Timmy", "last_name": "Turner", "role": "instructor"},
    {"id": 1001, "email": "student1@ucms.edu", "password_hash": "hashed_pass_s1", "first_name": "Elara", "last_name": "Vance", "role": "student", "university_id": "S1001A"},
    {"id": 1002, "email": "student2@ucms.edu", "password_hash": "hashed_pass_s2", "first_name": "Kaelen", "last_name": "Rix", "role": "student", "university_id": "S1002B"},
    {"id": 1003, "email": "student3@ucms.edu", "password_hash": "hashed_pass_s3", "first_name": "Jax", "last_name": "Teller", "role": "student", "university_id": "S1003C"},
]

MOCK_INSTRUCTORS = [
    {"instructor_id": 1, "department_code": "CS", "office_location": "B101", "office_hours": "Mon/Wed 10-12", "title": "Professor"},
    {"instructor_id": 2, "department_code": "ENG", "office_location": "E203", "office_hours": "Tue/Thu 14-16", "title": "Prof. Emeritus"},
    {"instructor_id": 3, "department_code": "MATH", "office_location": "M305", "office_hours": "By Appointment", "title": "Dr."},
]

MOCK_STUDENTS = [
    {"student_id": 1001, "enrollment_year": 2023, "major": "Computer Science", "expected_graduation": "Spring 2027", "gpa": 3.8, "current_standing": "Freshman"},
    {"student_id": 1002, "enrollment_year": 2023, "major": "Engineering", "expected_graduation": "Spring 2027", "gpa": 3.2, "current_standing": "Freshman"},
    {"student_id": 1003, "enrollment_year": 2022, "major": "Mathematics", "expected_graduation": "Spring 2026", "gpa": 3.5, "current_standing": "Sophomore"},
]

MOCK_COURSES = [
    {"course_id": "CS101", "course_code": "CS101", "course_name": "Fundamentals of Programming", "description": "Intro to Python. Foundational course for all majors.", "credits": 4, "academic_term": "Fall 2025", "max_capacity": 10, "instructor_id": 1},
    {"course_id": "CS205", "course_code": "CS205", "course_name": "Database Systems", "description": "Relational algebra, SQL, and database design. Core IT class.", "credits": 4, "academic_term": "Fall 2025", "max_capacity": 5, "instructor_id": 1},
    {"course_id": "ENG101", "course_code": "ENG101", "course_name": "Circuit Analysis", "description": "Basic electric circuits, Ohm's law.", "credits": 3, "academic_term": "Fall 2025", "max_capacity": 15, "instructor_id": 2},
    {"course_id": "MATH301", "course_code": "MATH301", "course_name": "Advanced Calculus", "description": "Differential equations and multivariate calculus.", "credits": 4, "academic_term": "Spring 2026", "max_capacity": 10, "instructor_id": 3},
    {"course_id": "CS400", "course_code": "CS400", "course_name": "Artificial Intelligence Concepts", "description": "A postgraduate level course exploring ML, neural networks, and AI ethics.", "credits": 4, "academic_term": "Fall 2025", "max_capacity": 8, "instructor_id": 3},
]

MOCK_PREREQS = [
    {"course_id": "CS205", "requires_course_id": "CS101"},
    {"course_id": "CS400", "requires_course_id": "CS205"},
]

MOCK_INITIAL_ENROLLMENTS = [
    {"student_id": 1001, "course_id": "CS101", "semester": "Fall 2025", "status": "Enrolled"},
    {"student_id": 1003, "course_id": "CS101", "semester": "Fall 2024", "final_grade": "A", "status": "Completed"},
]


# Initializes the database with mock data for all models.
def initialize_database():
    count_sql = text("SELECT COUNT(*) FROM users")
    user_count = db.session.execute(count_sql).scalar()
    
    if user_count == 0:
        for data in MOCK_USERS:
            db.session.add(User(**data))
        db.session.commit()
        
        for data in MOCK_INSTRUCTORS:
            db.session.add(Instructor(**data))
            
        for data in MOCK_STUDENTS:
            db.session.add(Student(**data))

        for data in MOCK_COURSES:
            db.session.add(Course(**data))
            
        for data in MOCK_PREREQS:
            db.session.add(Prerequisites(**data))
        db.session.commit()
        
        for data in MOCK_INITIAL_ENROLLMENTS:
            db.session.add(Enrollment(**data))
            if data.get('status') == 'Enrolled':
                update_sql = text("""
                    UPDATE courses 
                    SET current_enrollment = COALESCE(current_enrollment, 0) + 1 
                    WHERE course_id = :cid
                """)
                db.session.execute(update_sql, {"cid": data['course_id']})
                
        db.session.commit()
        print("Database initialized with mock data.")
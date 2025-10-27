from models import db, User, Student, Instructor, Course, Enrollment, Prerequisites, Assignment, Submission
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, or_, text
from typing import Dict, Any, List
from datetime import datetime

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


# Function for instructor name
def get_instructor_full_name_by_id(instructor_id):
    """Fetches an instructor's full name by their ID using raw SQL."""
    if not instructor_id:
        return "TBA"
    
    sql = text("SELECT first_name, last_name FROM user WHERE id = :id")
    result = db.session.execute(sql, {"id": instructor_id}).first()
    
    if result:
        return f"{result.first_name} {result.last_name}"
    return "TBA"

# Function for student's completed courses
def get_student_completed_courses(student_id):
    sql = text("""
        SELECT course_id FROM enrollment 
        WHERE student_id = :sid 
        AND status = 'Completed' 
        AND final_grade IS NOT NULL
    """)
    completed = db.session.execute(sql, {"sid": student_id}).all()
    return {c.course_id for c in completed}

# Checks if a student meets all prerequisites for a given course.
def check_prerequisites(student_id, course_id):
    sql = text("SELECT requires_course_id FROM prerequisites WHERE course_id = :cid")
    required_prereqs = db.session.execute(sql, {"cid": course_id}).all()

    if not required_prereqs:
        return True, []

    required_ids = {p.requires_course_id for p in required_prereqs}
    completed_ids = get_student_completed_courses(student_id) 
    missing_ids = list(required_ids - completed_ids)
    
    if missing_ids:
        return False, missing_ids
    else:
        return True, []

# Initializes the database with mock data for all models.
def initialize_database():
    count_sql = text("SELECT COUNT(*) FROM user")
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
                    UPDATE course 
                    SET current_enrollment = COALESCE(current_enrollment, 0) + 1 
                    WHERE course_id = :cid
                """)
                db.session.execute(update_sql, {"cid": data['course_id']})
                
        db.session.commit()
        print("Database initialized with mock data.")

# Handles the enrollment transaction with slot checking and prerequisite checking.
def enroll_student_in_course(student_id, course_id, semester="Fall 2025"):
    student_sql = text("""
        SELECT u.first_name 
        FROM student s 
        JOIN user u ON s.student_id = u.id 
        WHERE s.student_id = :sid
    """)
    student = db.session.execute(student_sql, {"sid": student_id}).first()
    
    course_sql = text("SELECT * FROM course WHERE course_id = :cid")
    course = db.session.execute(course_sql, {"cid": course_id}).first()

    if not student:
        raise ValueError("Student not found.")
    if not course:
        raise ValueError("Course not found.")

    if (course.current_enrollment or 0) >= course.max_capacity:
        raise ValueError("Course is full. Enrollment failed.")
    
    prereqs_met, missing = check_prerequisites(student_id, course_id)
    if not prereqs_met:
        raise ValueError(f"Prerequisites not met. Missing courses: {', '.join(missing)}")
    
    existing_sql = text("""
        SELECT 1 FROM enrollment 
        WHERE student_id = :sid AND course_id = :cid 
        AND status IN ('Enrolled', 'Waitlisted') 
        LIMIT 1
    """)
    existing_enrollment = db.session.execute(existing_sql, {"sid": student_id, "cid": course_id}).first()
    
    if existing_enrollment:
        raise ValueError("Student is already actively enrolled in this course.")

    try:
        insert_sql = text("""
            INSERT INTO enrollment (student_id, course_id, semester, status) 
            VALUES (:sid, :cid, :sem, 'Enrolled')
        """)
        db.session.execute(insert_sql, {"sid": student_id, "cid": course_id, "sem": semester})
        
        update_sql = text("""
            UPDATE course 
            SET current_enrollment = COALESCE(current_enrollment, 0) + 1 
            WHERE course_id = :cid
        """)
        db.session.execute(update_sql, {"cid": course_id})
        
        db.session.commit()
        return f"Successfully enrolled {student.first_name} in {course.course_code} - {course.course_name} for {semester}."
    
    except IntegrityError as e:
        db.session.rollback()
        print(e)
        raise ValueError("Database error occurred during enrollment.")

# Fetches all course prerequisites and maps them for quick lookup.
def get_prerequisites_map() -> Dict[str, List[str]]:

    prereqs_sql = text("SELECT course_id, requires_course_id FROM prerequisites")
    prereqs_results = db.session.execute(prereqs_sql).all()
    
    prereq_map = {}
    for p in prereqs_results:
        if p.course_id not in prereq_map:
            prereq_map[p.course_id] = []
        prereq_map[p.course_id].append(p.requires_course_id)
        
    # Return content: dict: {course_id: [requires_course_id, ...]}
    return prereq_map

def weighted_search_and_merge(
    weight: int, 
    conditions: str, 
    like_query: str, 
    final_results_map: Dict[str, Dict[str, Any]]
) -> None:

    sql = text(f"""
        SELECT 
            c.course_id, c.course_code, c.course_name, c.description,
            c.credits, c.academic_term, c.max_capacity, c.current_enrollment,
            u.first_name AS instructor_first, 
            u.last_name AS instructor_last
        FROM course c
        LEFT JOIN instructor i ON c.instructor_id = i.instructor_id
        LEFT JOIN user u ON i.instructor_id = u.id
        WHERE {conditions}
    """)
    
    matches = db.session.execute(sql, {"q": like_query}).all()
    
    for course in matches:
        course_id = course.course_id
        current_score = final_results_map.get(course_id, {}).get('relevance_score', 0)
        
        if weight > current_score:
            instructor_name = f"{course.instructor_first} {course.instructor_last}" if course.instructor_first else "TBA"
            slots_left = course.max_capacity - (course.current_enrollment or 0)
            
            final_results_map[course_id] = {
                "course_id": course_id,
                "course_code": course.course_code,
                "title": course.course_name,
                "description": course.description,
                "credits": course.credits,
                "academic_term": course.academic_term,
                "instructor_name": instructor_name,
                "slots_left": slots_left,
                "relevance_score": weight 
            }

# Performs a text search across course data, merging and display results based on weight.
def semantic_search(query: str) -> List[Dict[str, Any]]:

    query_lower = query.lower()
    like_query = f'%{query_lower}%'
    
    # Key: course_id, Value: {course_data, score}
    final_results_map = {}
    
    # Search 1: Course ID/Code (Weight: 5)
    weighted_search_and_merge(
        weight=5, 
        conditions="c.course_id ILIKE :q OR c.course_code ILIKE :q",
        like_query=like_query,
        final_results_map=final_results_map
    )

    # Search 2: Course Name (Weight: 3)
    weighted_search_and_merge(
        weight=3, 
        conditions="c.course_name ILIKE :q",
        like_query=like_query,
        final_results_map=final_results_map
    )

    # Search 3: Description and Instructor Name (Weight: 1)
    weighted_search_and_merge(
        weight=1, 
        conditions="c.description ILIKE :q OR u.first_name ILIKE :q OR u.last_name ILIKE :q",
        like_query=like_query,
        final_results_map=final_results_map
    )
        
    prereq_map = get_prerequisites_map()
    
    results_list = list(final_results_map.values())
    
    for result in results_list:
        course_id = result['course_id']
        prereqs = prereq_map.get(course_id, [])
        result["prerequisites"] = ", ".join(prereqs) if prereqs else "None"
    results_list.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results_list


# Fetches all courses with details.
def get_course_data():
    # NOTE: GROUP_CONCAT is SQLite specific. Use STRING_AGG for PostgreSQL or LISTAGG for Oracle.
    sql = text("""
        SELECT 
            c.*, 
            u.first_name AS instructor_first, 
            u.last_name AS instructor_last,
            (SELECT GROUP_CONCAT(pr.requires_course_id) 
             FROM prerequisites pr 
             WHERE pr.course_id = c.course_id) AS prereqs_list
        FROM course c
        LEFT JOIN instructor i ON c.instructor_id = i.instructor_id
        LEFT JOIN user u ON i.instructor_id = u.id
    """)
    courses = db.session.execute(sql).all()
    
    results = []
    for c in courses:
        if c.instructor_first:
            instructor_name = f"{c.instructor_first} {c.instructor_last}"
        else:
            instructor_name = "TBA"
            
        prereqs = c.prereqs_list.split(',') if c.prereqs_list else []

        results.append({
            "course_id": c.course_id,
            "course_code": c.course_code,
            "title": c.course_name,
            "description": c.description,
            "prerequisites": ", ".join(prereqs) if prereqs else "None",
            "credits": c.credits,
            "academic_term": c.academic_term,
            "max_capacity": c.max_capacity,
            "current_enrollment": c.current_enrollment,
            "slots_left": c.max_capacity - (c.current_enrollment or 0),
            "instructor_name": instructor_name
        })
    return results

# Fetches essential data for all students.
def get_student_data():
    sql = text("""
        SELECT s.student_id, u.university_id, u.first_name, u.last_name, s.major
        FROM student s
        JOIN user u ON s.student_id = u.id
    """)
    students = db.session.execute(sql).all()
    
    return [
        {
            "id": s.student_id,
            "university_id": s.university_id,
            "name": f"{s.first_name} {s.last_name}",
            "major": s.major
        } 
        for s in students
    ]

# Fetches essential data for all instructors.
def get_instructor_data():
    sql = text("""
        SELECT i.instructor_id, u.first_name, u.last_name, u.email, 
               i.department_code, i.title
        FROM instructor i
        JOIN user u ON i.instructor_id = u.id
    """)
    instructors = db.session.execute(sql).all()
    return [
        {
            "id": i.instructor_id,
            "name": f"{i.first_name} {i.last_name}",
            "email": i.email,
            "department_code": i.department_code,
            "title": i.title
        } 
        for i in instructors
    ]

# Fetches all users for client-side login verification.
def get_user_data():
    sql = text("SELECT id, email, first_name, last_name, role FROM user")
    users = db.session.execute(sql).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "name": f"{u.first_name} {u.last_name}", 
            "role": u.role,
        }
        for u in users
    ]

# Fetches detailed student data using the linked User ID.
def get_student_details_by_user_id(user_id):
    sql = text("SELECT student_id, enrollment_year, major FROM student WHERE student_id = :uid")
    student = db.session.execute(sql, {"uid": user_id}).first()
    
    if student:
        return {
            "id": student.student_id, 
            "enrollment_year": student.enrollment_year,
            "major": student.major,
        }
    return None

# Fetches detailed instructor data using the linked User ID.
def get_instructor_details_by_user_id(user_id):
    sql = text("SELECT instructor_id, department_code, title FROM instructor WHERE instructor_id = :uid")
    instructor = db.session.execute(sql, {"uid": user_id}).first()
    
    if instructor:
        return {
            "id": instructor.instructor_id, 
            "department_code": instructor.department_code,
            "title": instructor.title,
        }
    return None

# Retrieves the instructor's full name, handling missing records.
def get_instructor_full_name(course):
    if hasattr(course, 'instructor') and course.instructor and course.instructor.user:
        return f"{course.instructor.user.first_name} {course.instructor.user.last_name}"
    elif hasattr(course, 'instructor_id') and course.instructor_id:
        return get_instructor_full_name_by_id(course.instructor_id)
    return "TBA"

# Fetches currently enrolled courses for a given student ID.
def get_student_enrollments(student_id):
    sql = text("""
        SELECT 
            c.course_id, c.course_name, c.credits, c.academic_term,
            e.semester,
            u.first_name AS instructor_first, 
            u.last_name AS instructor_last
        FROM enrollment e
        JOIN course c ON e.course_id = c.course_id
        LEFT JOIN instructor i ON c.instructor_id = i.instructor_id
        LEFT JOIN user u ON i.instructor_id = u.id
        WHERE e.student_id = :sid AND e.status = 'Enrolled'
    """)
    enrollments = db.session.execute(sql, {"sid": student_id}).all()

    results = []
    for enrollment in enrollments:
        if enrollment.instructor_first:
            instructor_name = f"{enrollment.instructor_first} {enrollment.instructor_last}"
        else:
            instructor_name = "TBA"
        
        results.append({
            "course_id": enrollment.course_id,
            "title": enrollment.course_name,
            "credits": enrollment.credits,
            "academic_term": enrollment.academic_term,
            "instructor_name": instructor_name,
            "semester": enrollment.semester,
        })
    
    return results

# Fetches all courses taught by a specific instructor ID.
def get_instructor_courses(instructor_id):
    sql = text("""
        SELECT course_id, course_code, course_name, description, 
               credits, max_capacity, COALESCE(current_enrollment, 0) AS current_enrollment
        FROM course 
        WHERE instructor_id = :iid
    """)
    courses = db.session.execute(sql, {"iid": instructor_id}).all()
    
    return [
        {
            "course_id": c.course_id,
            "course_code": c.course_code,
            "title": c.course_name,
            "description": c.description,
            "credits": c.credits,
            "max_capacity": c.max_capacity,
            "current_enrollment": c.current_enrollment
        }
        for c in courses
    ]

# Fetches list of actively enrolled students and their details in a course.
def get_students_in_course(course_id): 
    sql = text("""
        SELECT 
            s.student_id, 
            u.first_name, 
            u.last_name, 
            s.major, 
            u.university_id
        FROM student s
        JOIN enrollment e ON s.student_id = e.student_id
        JOIN user u ON s.student_id = u.id
        WHERE e.course_id = :cid AND e.status = 'Enrolled'
    """)
    students = db.session.execute(sql, {"cid": course_id}).all()
    
    return [
        {
            "id": s.student_id,
            "name": f"{s.first_name} {s.last_name}",
            "major": s.major,
            "university_id": s.university_id
        }
        for s in students
    ]
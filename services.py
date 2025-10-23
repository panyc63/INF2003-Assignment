from models import db, User, Student, Instructor, Course, Enrollment, Prerequisites, Assignment, Submission
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy import func, or_

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


# Returns a set of course_ids a student has successfully completed.
def get_student_completed_courses(student_id):
    completed = db.session.query(Enrollment.course_id).filter(
        Enrollment.student_id == student_id,
        Enrollment.status == 'Completed',
        Enrollment.final_grade.isnot(None)
    ).all()
    return {c[0] for c in completed}

# Checks if a student meets all prerequisites for a given course.
def check_prerequisites(student_id, course_id):
    required_prereqs = db.session.query(Prerequisites.requires_course_id).filter(
        Prerequisites.course_id == course_id
    ).all()

    if not required_prereqs:
        return True, []

    required_ids = {p[0] for p in required_prereqs}
    completed_ids = get_student_completed_courses(student_id)

    missing_ids = list(required_ids - completed_ids)
    
    if missing_ids:
        return False, missing_ids
    else:
        return True, []

# Initializes the database with mock data for all models.
def initialize_database():
    if User.query.count() == 0:
        
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
                course = Course.query.get(data['course_id'])
                if course:
                    course.current_enrollment = (course.current_enrollment or 0) + 1
            
        db.session.commit()
        print("Database initialized with mock data.")

# Handles the enrollment transaction with slot checking and prerequisite checking.
def enroll_student_in_course(student_id, course_id, semester="Fall 2025"):
    student = Student.query.get(student_id)
    course = Course.query.get(course_id)

    if not student:
        raise ValueError("Student not found.")
    if not course:
        raise ValueError("Course not found.")

    if course.current_enrollment >= course.max_capacity:
        raise ValueError("Course is full. Enrollment failed.")
    
    prereqs_met, missing = check_prerequisites(student_id, course_id)
    if not prereqs_met:
        raise ValueError(f"Prerequisites not met. Missing courses: {', '.join(missing)}")
    
    existing_enrollment = Enrollment.query.filter(
        Enrollment.student_id == student_id, 
        Enrollment.course_id == course_id,
        Enrollment.status.in_(['Enrolled', 'Waitlisted']) 
    ).first()
    
    if existing_enrollment:
        raise ValueError("Student is already actively enrolled in this course.")

    try:
        new_enrollment = Enrollment(
            student_id=student_id, 
            course_id=course_id,
            semester=semester,
            status='Enrolled'
        )
        db.session.add(new_enrollment)
        
        course.current_enrollment += 1
        
        db.session.commit()
        return f"Successfully enrolled {student.user.first_name} in {course.course_code} - {course.course_name} for {semester}."
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Database error occurred during enrollment.")

# Performs a dynamic text search across course data using database lookups for expansion.
def semantic_search(query):
    query_lower = query.lower()
    
    initial_terms = set(query_lower.split())
    expanded_search_terms = set(initial_terms)
    
    instructor_matches = db.session.query(User.first_name, User.last_name).join(
        Instructor, User.id == Instructor.instructor_id
    ).filter(
        or_(
            User.first_name.ilike(f'%{query_lower}%'),
            User.last_name.ilike(f'%{query_lower}%'),
            Instructor.department_code.ilike(f'%{query_lower}%')
        )
    ).all()
    
    for first_name, last_name in instructor_matches:
        expanded_search_terms.add(first_name.lower())
        expanded_search_terms.add(last_name.lower())

    course_code_matches = Course.query.filter(
        or_(
            Course.course_code.ilike(f'%{query_lower}%'),
            Course.course_id.ilike(f'%{query_lower}%')
        )
    ).all()

    for course in course_code_matches:
        expanded_search_terms.update([word for word in course.course_name.lower().split() if len(word) > 2])
        expanded_search_terms.update([word for word in course.description.lower().split() if len(word) > 2])

    final_search_terms = [term for term in expanded_search_terms if len(term) > 2]
    
    results = []
    all_courses = Course.query.all()
    
    for course in all_courses:
        instructor_name = get_instructor_full_name(course)
        course_text = f"{course.course_id} {course.course_name} {course.description} {course.course_code} {instructor_name}".lower()
        
        score = 0
        for term in final_search_terms:
            if term in course_text:
                score += 1

        if score > 0:
            slots_left = course.max_capacity - (course.current_enrollment or 0)
            
            prereqs = [p.requires_course_id for p in course.prerequisites]

            results.append({
                "course_id": course.course_id,
                "course_code": course.course_code,
                "title": course.course_name,
                "description": course.description,
                "prerequisites": ", ".join(prereqs) if prereqs else "None",
                "credits": course.credits,
                "academic_term": course.academic_term,
                "instructor_name": instructor_name,
                "slots_left": slots_left,
                "relevance_score": score
            })

    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results

# Fetches all courses with details.
def get_course_data():
    courses = Course.query.all()
    return [
        {
            "course_id": c.course_id,
            "course_code": c.course_code,
            "title": c.course_name,
            "description": c.description,
            "prerequisites": ", ".join([p.requires_course_id for p in c.prerequisites]) if c.prerequisites else "None",
            "credits": c.credits,
            "academic_term": c.academic_term,
            "max_capacity": c.max_capacity,
            "current_enrollment": c.current_enrollment,
            "slots_left": c.max_capacity - (c.current_enrollment or 0),
            "instructor_name": get_instructor_full_name(c)
        }
        for c in courses
    ]

# Fetches essential data for all students.
def get_student_data():
    students = db.session.query(Student, User).join(User).all()
    return [
        {
            "id": s.student_id,
            "university_id": u.university_id,
            "name": f"{u.first_name} {u.last_name}",
            "major": s.major
        } 
        for s, u in students
    ]

# Fetches essential data for all instructors.
def get_instructor_data():
    instructors = db.session.query(Instructor, User).join(User).all()
    return [
        {
            "id": i.instructor_id,
            "name": f"{u.first_name} {u.last_name}",
            "email": u.email,
            "department_code": i.department_code,
            "title": i.title
        } 
        for i, u in instructors
    ]

# Fetches all users for client-side login verification.
def get_user_data():
    users = User.query.all()
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
    student = Student.query.filter_by(student_id=user_id).first()
    
    if student:
        return {
            "id": student.student_id, 
            "enrollment_year": student.enrollment_year,
            "major": student.major,
        }
    return None

# Fetches detailed instructor data using the linked User ID.
def get_instructor_details_by_user_id(user_id):
    instructor = Instructor.query.filter_by(instructor_id=user_id).first()
    
    if instructor:
        return {
            "id": instructor.instructor_id, 
            "department_code": instructor.department_code,
            "title": instructor.title,
        }
    return None

# Retrieves the instructor's full name, handling missing records.
def get_instructor_full_name(course):
    if course.instructor and course.instructor.user:
        return f"{course.instructor.user.first_name} {course.instructor.user.last_name}"
    return "TBA"

# Fetches currently enrolled courses for a given student ID.
def get_student_enrollments(student_id):
    enrollments = db.session.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.status == 'Enrolled'
    ).all()

    results = []
    for enrollment in enrollments:
        course = enrollment.course
        instructor_name = get_instructor_full_name(course)
        
        results.append({
            "course_id": course.course_id,
            "title": course.course_name,
            "credits": course.credits,
            "academic_term": course.academic_term,
            "instructor_name": instructor_name,
            "semester": enrollment.semester,
        })
    
    return results

# Fetches all courses taught by a specific instructor ID.
def get_instructor_courses(instructor_id):
    courses = Course.query.filter_by(instructor_id=instructor_id).all()
    
    return [
        {
            "course_id": c.course_id,
            "course_code": c.course_code,
            "title": c.course_name,
            "description": c.description,
            "credits": c.credits,
            "max_capacity": c.max_capacity,
            "current_enrollment": c.current_enrollment or 0
        }
        for c in courses
    ]

# Fetches list of actively enrolled students and their details in a course.
def get_students_in_course(course_id): 
    students = db.session.query(Student, User).join(Enrollment, Student.student_id == Enrollment.student_id).join(User, Student.student_id == User.id).filter(
        Enrollment.course_id == course_id,
        Enrollment.status == 'Enrolled'
    ).all()
    
    return [
        {
            "id": s.student_id,
            "name": f"{u.first_name} {u.last_name}",
            "major": s.major,
            "university_id": u.university_id
        }
        for s, u in students
    ]
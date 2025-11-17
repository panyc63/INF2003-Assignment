from .. import db, mongo
from ..models import User, Student, Instructor, Course, Enrollment, Prerequisites, Assignment, Submission
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, or_, text
from sqlalchemy.orm import joinedload, aliased
from typing import Dict, Any, List
from datetime import datetime
def get_course_details_by_ids_list(course_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetches full, rich course details for a specific list of course IDs
    using the SQLAlchemy ORM.
    """
    if not course_ids:
        return []

    # --- This is a more advanced ORM query ---
    # 1. We alias User to avoid name conflicts
    InstructorUser = aliased(User)
    
    # 2. We query the Course model
    courses = db.session.query(Course)\
        .filter(Course.course_id.in_(course_ids))\
        .options(
            # 3. We "join" the related tables to get instructor info
            joinedload(Course.instructor)
            .joinedload(Instructor.user.of_type(InstructorUser))
        ).all()

    # 4. We build the same rich JSON as your get_course_data function
    results = []
    for c in courses:
        instructor_name = "TBA"
        if c.instructor and c.instructor.user:
            instructor_name = f"{c.instructor.user.first_name} {c.instructor.user.last_name}"
        
        # We don't need prerequisites here, but you could add them
        
        results.append({
            "course_id": c.course_id,
            "course_code": c.course_code,
            "course_name": c.course_name,
            "description": c.description,
            "prerequisites": "None", # Add logic if needed
            "credits": c.credits,
            "academic_term": c.academic_term,
            "max_capacity": c.max_capacity,
            "current_enrollment": c.current_enrollment,
            "slots_left": c.max_capacity - (c.current_enrollment or 0),
            "instructor_name": instructor_name
        })

    # --- Re-order the results to match the semantic search score ---
    # Create a map for quick lookup
    results_map = {r['course_id']: r for r in results}
    # Return in the order provided by course_ids
    ordered_results = [results_map[id] for id in course_ids if id in results_map]
    
    return ordered_results
# Function for instructor name
def get_instructor_full_name_by_id(instructor_id):
    """Fetches an instructor's full name by their ID using raw SQL."""
    if not instructor_id:
        return "TBA"
    
    sql = text("SELECT first_name, last_name FROM users WHERE id = :id")
    result = db.session.execute(sql, {"id": instructor_id}).first()
    
    if result:
        return f"{result.first_name} {result.last_name}"
    return "TBA"

# Function for student's completed courses
def get_student_completed_courses(student_id):
    sql = text("""
        SELECT course_id FROM enrollments 
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

# Handles the enrollment transaction with slot checking and prerequisite checking.
def enroll_student_in_course(student_id, course_id, semester="Fall 2025"):
    student_sql = text("""
        SELECT u.first_name 
        FROM students s 
        JOIN users u ON s.student_id = u.user_id 
        WHERE s.student_id = :sid
    """)
    student = db.session.execute(student_sql, {"sid": student_id}).first()
    
    course_sql = text("SELECT * FROM courses WHERE course_id = :cid")
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
        SELECT 1 FROM enrollments 
        WHERE student_id = :sid AND course_id = :cid 
        AND status IN ('Enrolled', 'Waitlisted') 
        LIMIT 1
    """)
    existing_enrollment = db.session.execute(existing_sql, {"sid": student_id, "cid": course_id}).first()
    
    if existing_enrollment:
        raise ValueError("Student is already actively enrolled in this course.")

    try:
        insert_sql = text("""
            INSERT INTO enrollments (student_id, course_id, semester, status) 
            VALUES (:sid, :cid, :sem, 'Enrolled')
        """)
        db.session.execute(insert_sql, {"sid": student_id, "cid": course_id, "sem": semester})
        
        update_sql = text("""
            UPDATE courses 
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
    
def drop_student_enrollment(student_id, course_id):
    """
    Deletes an active enrollment from the database (instead of marking Dropped)
    and decrements the course's current_enrollment counter.
    Only deletes if the student is currently 'Enrolled'.
    """

    # Check if the student is actually enrolled
    check_sql = text("""
        SELECT 1 FROM enrollments
        WHERE student_id = :sid
          AND course_id  = :cid
          AND status     = 'Enrolled'
        LIMIT 1
    """)
    enrollment = db.session.execute(check_sql, {"sid": student_id, "cid": course_id}).first()

    if not enrollment:
        raise ValueError("You are not currently enrolled in this course.")

    try:
        # DELETE the enrollment row
        delete_sql = text("""
            DELETE FROM enrollments
            WHERE student_id = :sid
              AND course_id  = :cid
              AND status     = 'Enrolled'
        """)
        db.session.execute(delete_sql, {"sid": student_id, "cid": course_id})

        # Decrement seat count
        update_course_sql = text("""
            UPDATE courses
            SET current_enrollment =
                CASE 
                    WHEN current_enrollment IS NULL OR current_enrollment <= 0 THEN 0
                    ELSE current_enrollment - 1
                END
            WHERE course_id = :cid
        """)
        db.session.execute(update_course_sql, {"cid": course_id})

        db.session.commit()
        return f"Successfully dropped {course_id}."
    
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Database error occurred while dropping the course.")

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
    search_pattern: str, 
    final_results_map: Dict[str, Dict[str, Any]]
) -> None:

    # Retrieve course taught by specific instructor with flexible condition
    sql = text(f"""
        SELECT 
            c.course_id, c.course_code, c.course_name, c.description,
            c.credits, c.academic_term, c.max_capacity, c.current_enrollment,
            u.first_name AS instructor_first, 
            u.last_name AS instructor_last
        FROM courses c
        LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
        LEFT JOIN users u ON i.instructor_id = u.user_id
        WHERE {conditions}
    """)
    
    matches = db.session.execute(sql, {"q": search_pattern}).all()
    
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
                'max_capacity': course.max_capacity,
                "slots_left": slots_left,
                "relevance_score": weight 
            }

# Performs a text search across course data, merging and display results based on weight.
def semantic_search(query: str) -> List[Dict[str, Any]]:

    query_lower = query.lower()
    search_pattern = f'%{query_lower}%'
    
    # Key: course_id, Value: {course_data, score}
    final_results_map = {}
    
    # Search 1: Course ID/Code (Weight: 5)
    weighted_search_and_merge(
        weight=5, 
        conditions="c.course_id LIKE :q OR c.course_code LIKE :q",
        search_pattern=search_pattern,
        final_results_map=final_results_map
    )

    # Search 2: Course Name (Weight: 3)
    weighted_search_and_merge(
        weight=3, 
        conditions="c.course_name LIKE :q",
        search_pattern=search_pattern,
        final_results_map=final_results_map
    )

    # Search 3: Description and Instructor Name (Weight: 1)
    weighted_search_and_merge(
        weight=1, 
        conditions="c.description LIKE :q OR u.first_name LIKE :q OR u.last_name LIKE :q",
        search_pattern=search_pattern,
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
        FROM courses c
        LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
        LEFT JOIN users u ON i.instructor_id = u.user_id
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
            "course_name": c.course_name,
            "description": c.description,
            "prerequisites": ", ".join(prereqs) if prereqs else "None",
            "credits": c.credits,
            "academic_term": c.academic_term,
            "max_capacity": c.max_capacity,
            "current_enrollment": c.current_enrollment,
            "slots_left": c.max_capacity - (c.current_enrollment or 0),
            "instructor_name": instructor_name,
            "created_at": c.created_at.isoformat() if c.created_at else None
        })
        print(results)
    return results

def get_course_details_by_id(course_id):
    sql = text("""
        SELECT course_id, course_name, credits, description, academic_term
        FROM courses 
        WHERE course_id = :cid
    """)
    course = db.session.execute(sql, {"cid": course_id}).first()
    
    if course:
        return {
            "course_id": course.course_id, 
            "course_name": course.course_name,
            "credits": course.credits,
            "description": course.description,
            "academic_term": course.academic_term,
        }
    return None

# Fetches essential data for all students.
def get_student_data():
    sql = text("""
        SELECT s.student_id, u.university_id, u.first_name, u.last_name, s.major
        FROM students s
        JOIN users u ON s.student_id = u.user_id
    """)
    students = db.session.execute(sql).all()
    print(students)
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
        FROM instructors i
        JOIN users u ON i.instructor_id = u.user_id
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
    sql = text("SELECT user_id, email, first_name, last_name, role FROM users")
    users = db.session.execute(sql).all()
    return [
        {
            "id": u.user_id,
            "email": u.email,
            "name": f"{u.first_name} {u.last_name}", 
            "role": u.role,
        }
        for u in users
    ]

# Fetches detailed student data using the linked User ID.
def get_student_details_by_user_id(user_id):
    sql = text("SELECT student_id, enrollment_year, major FROM students WHERE student_id = :uid")
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
    sql = text("SELECT instructor_id, department_code, title FROM instructors WHERE instructor_id = :uid")
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
# Fetches currently enrolled courses for a given student ID.
def get_student_enrollments(student_id):
    sql = text("""
        SELECT 
            c.course_id, c.course_name, c.credits, c.academic_term,
            e.semester,
            e.status,
            e.final_grade,
            u.first_name AS instructor_first, 
            u.last_name AS instructor_last
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
        LEFT JOIN users u ON i.instructor_id = u.user_id
        WHERE e.student_id = :sid AND (e.status = 'Enrolled' OR e.status = 'Completed') -- Get all records
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
            "course_name": enrollment.course_name,
            "credits": enrollment.credits,
            "academic_term": enrollment.academic_term,
            "instructor_name": instructor_name,
            "semester": enrollment.semester,
            "status": enrollment.status,
            "final_grade": enrollment.final_grade
        })
    
    return results

# Fetches all courses taught by a specific instructor ID.
def get_instructor_courses(instructor_id):
    sql = text("""
        SELECT course_id, course_code, course_name, description, 
               credits, max_capacity, COALESCE(current_enrollment, 0) AS current_enrollment
        FROM courses 
        WHERE instructor_id = :iid
    """)
    courses = db.session.execute(sql, {"iid": instructor_id}).all()
    
    return [
        {
            "course_id": c.course_id,
            "course_code": c.course_code,
            "course_name": c.course_name,
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
        FROM students s
        JOIN enrollments e ON s.student_id = e.student_id
        JOIN users u ON s.student_id = u.user_id
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
    
# ADMIN FUNCTIONS HERE
# =====================================================
# ADMIN SERVICES: Course Management (CRUD)
# =====================================================

def create_course(data):
    """Creates a new course."""
    try:
        # Basic validation
        if not data.get('course_id') or not data.get('course_name'):
            raise ValueError("Course ID and Name are required.")

        sql = text("""
            INSERT INTO courses (course_id, course_code, course_name, description, credits, academic_term, max_capacity, instructor_id)
            VALUES (:id, :code, :name, :desc, :credits, :term, :cap, :inst_id)
        """)
        
        db.session.execute(sql, {
            "id": data['course_id'],
            "code": data.get('course_code', data['course_id']), # Default code to ID if missing
            "name": data['course_name'],
            "desc": data.get('description', ''),
            "credits": data.get('credits', 6),
            "term": data.get('academic_term', 'Fall 2025'),
            "cap": data.get('max_capacity', 30),
            "inst_id": data.get('instructor_id') # Can be None
        })
        db.session.commit()
        return f"Course {data['course_id']} created successfully."
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Course ID {data['course_id']} already exists.")
    except Exception as e:
        db.session.rollback()
        raise e

def update_course(course_id, data):
    """Updates an existing course."""
    sql = text("""
        UPDATE courses 
        SET course_name = :name, 
            description = :desc, 
            credits = :credits, 
            academic_term = :term, 
            max_capacity = :cap,
            instructor_id = :inst_id
        WHERE course_id = :id
    """)
    
    result = db.session.execute(sql, {
        "id": course_id,
        "name": data['course_name'],
        "desc": data.get('description'),
        "credits": data.get('credits'),
        "term": data.get('academic_term'),
        "cap": data.get('max_capacity'),
        "inst_id": data.get('instructor_id')
    })
    db.session.commit()
    
    if result.rowcount == 0:
        raise ValueError("Course not found.")
    return f"Course {course_id} updated."

def delete_course(course_id):
    """Deletes a course."""
    # Note: Cascading delete in SQL will handle enrollments/assignments
    sql = text("DELETE FROM courses WHERE course_id = :id")
    result = db.session.execute(sql, {"id": course_id})
    db.session.commit()
    
    if result.rowcount == 0:
        raise ValueError("Course not found.")
    return f"Course {course_id} deleted."

# =====================================================
# ADMIN SERVICES: User Management
# =====================================================

def get_all_users_detailed():
    """Fetches users with role-specific details for the Admin table."""
    sql = text("""
        SELECT 
            u.user_id, u.university_id, u.first_name, u.last_name, u.email, u.role, u.is_active,
            s.major,
            i.department_code
        FROM users u
        LEFT JOIN students s ON u.user_id = s.student_id
        LEFT JOIN instructors i ON u.user_id = i.instructor_id
        ORDER BY u.date_joined DESC
    """)
    users = db.session.execute(sql).all()
    
    return [
        {
            "user_id": u.user_id,
            "university_id": u.university_id,
            "name": f"{u.first_name} {u.last_name}",
            "email": u.email,
            "role": u.role,
            "is_active": bool(u.is_active),
            "details": u.major if u.role == 'student' else (u.department_code if u.role == 'instructor' else 'Admin')
        }
        for u in users
    ]

def toggle_user_status(user_id):
    """Toggles a user between active and inactive."""
    sql = text("UPDATE users SET is_active = NOT is_active WHERE user_id = :uid")
    db.session.execute(sql, {"uid": user_id})
    db.session.commit()
    return "User status updated."

# =====================================================
# ADMIN SERVICES: User CRUD
# =====================================================

def create_user(data):
    """Creates a user and their role-specific profile (Student/Instructor)."""
    try:
        # 1. Validate Basic Info
        if not data.get('university_id') or not data.get('email'):
            raise ValueError("University ID and Email are required.")
            
        role = data.get('role', 'student')
        
        # 2. Insert into Base Users Table
        # Note: In a real app, hash the password here!
        sql_user = text("""
            INSERT INTO users (university_id, email, password_hash, first_name, last_name, role, is_active)
            VALUES (:uid, :email, :pwd, :fname, :lname, :role, 1)
        """)
        
        db.session.execute(sql_user, {
            "uid": data['university_id'],
            "email": data['email'],
            "pwd": "default_password", # Set a default or allow input
            "fname": data['first_name'],
            "lname": data['last_name'],
            "role": role
        })
        
        # 3. Get the new auto-incremented user_id
        # (Last inserted ID retrieval depends on DB, but we can query by unique university_id)
        user_id_sql = text("SELECT user_id FROM users WHERE university_id = :uid")
        user_record = db.session.execute(user_id_sql, {"uid": data['university_id']}).first()
        new_user_id = user_record.user_id

        # 4. Insert Role-Specific Data
        if role == 'student':
            sql_student = text("""
                INSERT INTO students (student_id, enrollment_year, major, current_standing, gpa)
                VALUES (:id, :year, :major, :standing, 0.0)
            """)
            db.session.execute(sql_student, {
                "id": new_user_id,
                "year": data.get('enrollment_year', 2025),
                "major": data.get('major', 'Undeclared'),
                "standing": 'Year 1'
            })
            
        elif role == 'instructor':
            sql_instructor = text("""
                INSERT INTO instructors (instructor_id, department_code, title, office_location)
                VALUES (:id, :dept, :title, :office)
            """)
            db.session.execute(sql_instructor, {
                "id": new_user_id,
                "dept": data.get('department_code', 'GEN'),
                "title": data.get('title', 'Lecturer'),
                "office": data.get('office_location', 'TBA')
            })

        db.session.commit()
        return f"User {data['university_id']} created successfully."

    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"User with ID {data['university_id']} or Email already exists.")
    except Exception as e:
        db.session.rollback()
        raise e

def update_user(user_id, data):
    """Updates user details and role-specific data."""
    try:
        # 1. Update Base User
        sql_user = text("""
            UPDATE users 
            SET first_name = :fname, last_name = :lname, email = :email
            WHERE user_id = :id
        """)
        db.session.execute(sql_user, {
            "fname": data['first_name'],
            "lname": data['last_name'],
            "email": data['email'],
            "id": user_id
        })

        role = data.get('role')

        # 2. Update Child Tables based on Role
        if role == 'student':
            sql_student = text("""
                UPDATE students 
                SET major = :major, enrollment_year = :year
                WHERE student_id = :id
            """)
            db.session.execute(sql_student, {
                "major": data.get('major'),
                "year": data.get('enrollment_year'),
                "id": user_id
            })
        elif role == 'instructor':
            sql_instructor = text("""
                UPDATE instructors
                SET department_code = :dept, title = :title
                WHERE instructor_id = :id
            """)
            db.session.execute(sql_instructor, {
                "dept": data.get('department_code'),
                "title": data.get('title'),
                "id": user_id
            })

        db.session.commit()
        return f"User {user_id} updated."
    except Exception as e:
        db.session.rollback()
        raise e

def delete_user(user_id):
    """Deletes a user (Cascade deletes student/instructor profile)."""
    # The SQL Schema uses ON DELETE CASCADE, so deleting the parent 'users' row is enough.
    sql = text("DELETE FROM users WHERE user_id = :id")
    result = db.session.execute(sql, {"id": user_id})
    db.session.commit()
    
    if result.rowcount == 0:
        raise ValueError("User not found.")
    return f"User {user_id} deleted."

# Helper to get single user details for Edit Modal
def get_user_full_details(user_id):
    sql = text("""
        SELECT 
            u.*,
            s.major, s.enrollment_year,
            i.department_code, i.title
        FROM users u
        LEFT JOIN students s ON u.user_id = s.student_id
        LEFT JOIN instructors i ON u.user_id = i.instructor_id
        WHERE u.user_id = :id
    """)
    row = db.session.execute(sql, {"id": user_id}).first()
    if not row: 
        return None
    
    # Convert SQLAlchemy Row to Dict
    return {
        "user_id": row.user_id,
        "university_id": row.university_id,
        "first_name": row.first_name,
        "last_name": row.last_name,
        "email": row.email,
        "role": row.role,
        # Role specific
        "major": row.major,
        "enrollment_year": row.enrollment_year,
        "department_code": row.department_code,
        "title": row.title
    }
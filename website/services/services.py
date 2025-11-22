from . import services_sql as sql_service
from . import services_mongo as mongo_service

# Global variable to track the active provider
CURRENT_PROVIDER = "sql"
_active_service = sql_service


def set_db_provider(provider_name):
    """Switches the backend service module."""
    global CURRENT_PROVIDER, _active_service

    if provider_name == "mongodb":
        CURRENT_PROVIDER = "mongodb"
        _active_service = mongo_service
        print("--> Switched to MongoDB Service")
    else:
        CURRENT_PROVIDER = "sql"
        _active_service = sql_service
        print("--> Switched to SQL Service")


# ========================================================
#  WRAPPER FUNCTIONS (Forward calls to active service)
# ========================================================


def get_module_data():
    return _active_service.get_module_data()


def get_module_details_by_id(module_id, student_id=None):
    return _active_service.get_module_details_by_id(module_id, student_id)


def create_module(data):
    return _active_service.create_module(data)


def update_module(module_id, data):
    return _active_service.update_module(module_id, data)


def delete_module(module_id):
    return _active_service.delete_module(module_id)


def get_module_details_by_ids_list(module_ids):
    return _active_service.get_module_details_by_ids_list(module_ids)



def get_all_users_detailed():
    return _active_service.get_all_users_detailed()


def create_user(data):
    return _active_service.create_user(data)


def update_user(user_id, data):
    return _active_service.update_user(user_id, data)


def delete_user(user_id):
    return _active_service.delete_user(user_id)


def get_user_full_details(user_id):
    return _active_service.get_user_full_details(user_id)


def toggle_user_status(user_id):
    return _active_service.toggle_user_status(user_id)


def enroll_student_in_module(student_id, module_id):
    return _active_service.enroll_student_in_module(student_id, module_id)


def drop_student_enrollment_module(student_id, module_id):
    return _active_service.drop_student_enrollment_module(student_id, module_id)


def get_student_enrollments(student_id):
    return _active_service.get_student_enrollments(student_id)


# --- Pass-throughs for less critical functions ---
        return True, []

# Handles the enrollment transaction with slot checking and prerequisite checking.
def enroll_student_in_course(student_id, course_id):
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
            INSERT INTO enrollments (student_id, course_id, status) 
            VALUES (:sid, :cid, 'Enrolled')
        """)
        db.session.execute(insert_sql, {"sid": student_id, "cid": course_id})
        
        update_sql = text("""
            UPDATE courses 
            SET current_enrollment = COALESCE(current_enrollment, 0) + 1 
            WHERE course_id = :cid
        """)
        db.session.execute(update_sql, {"cid": course_id})
        
        db.session.commit()
        return f"Successfully enrolled {student.first_name} in {course.course_id} - {course.course_name}."
    
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
            c.course_id, c.course_name, c.description,
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
        conditions="c.course_id LIKE :q",
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

def get_course_details_by_id(course_id, student_id=None):
    """
    Fetches comprehensive details for a single course, including 
    instructor name, enrollment counts, and prerequisites.
    """
    sql = text("""
        SELECT 
            c.*, 
            u.first_name AS instructor_first, 
            u.last_name AS instructor_last,
            (SELECT GROUP_CONCAT(pr.requires_course_id SEPARATOR ', ') 
             FROM prerequisites pr 
             WHERE pr.course_id = c.course_id) AS prereqs_list
        FROM courses c
        LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
        LEFT JOIN users u ON i.instructor_id = u.user_id
        WHERE c.course_id = :cid
    """)
    
    course = db.session.execute(sql, {"cid": course_id}).first()
    
    if course:
        # robust name handling
        if course.instructor_first:
            instructor_name = f"{course.instructor_first} {course.instructor_last}"
        else:
            instructor_name = "TBA"

        # handle enrollment math
        curr = course.current_enrollment or 0
        cap = course.max_capacity
        
        return {
            "course_id": course.course_id, 
            "course_name": course.course_name,
            "credits": course.credits,
            "description": course.description,
            "academic_term": course.academic_term,
            "max_capacity": cap,
            "current_enrollment": curr,
            "slots_left": cap - curr,
            "instructor_name": instructor_name,
            "prerequisites": course.prereqs_list if course.prereqs_list else "None"
        }
    return None

# Fetches essential data for all students.
def get_student_data():
    return _active_service.get_student_data()


def get_instructor_data():
    return _active_service.get_instructor_data()


def get_user_data():
    return _active_service.get_user_data()


def get_student_details_by_user_id(uid):
    return _active_service.get_student_details_by_user_id(uid)


def get_instructor_details_by_user_id(uid):
    return _active_service.get_instructor_details_by_user_id(uid)


def get_instructor_modules(iid):
    return _active_service.get_instructor_modules(iid)


def get_students_in_module(cid):
    return _active_service.get_students_in_module(cid)

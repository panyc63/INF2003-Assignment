from flask import Blueprint, request, jsonify
# --- New Imports for NoSQL Search ---
from website import mongo
from sentence_transformers import SentenceTransformer
# -------------------------------------
from ..services.services import (
    get_course_data,
    # semantic_search,  <-- We removed this old SQL search
    get_course_details_by_id, # <-- Added this for the single course route
    get_student_data,
    get_student_enrollments,
    enroll_student_in_course,
    get_user_data,
    get_student_details_by_user_id,
    get_instructor_details_by_user_id,
    get_instructor_courses,
    get_students_in_course,
    get_course_details_by_ids_list,
    drop_student_enrollment,
)

#api blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- Load the NLP model once ---
model = SentenceTransformer('all-MiniLM-L6-v2')
# -------------------------------


# Retrieve all course data including instructor name and slots remaining.
@api_bp.route('/courses', methods=['GET'])
def get_courses():
    all_courses = get_course_data()
    return jsonify(all_courses)

# Retrieve all course data including instructor name and slots remaining.
@api_bp.route('/courses/<string:course_id>', methods=['GET'])
def get_course(course_id):
    # --- FIX: Use the correct function for a single course ---
    course = get_course_details_by_id(course_id)
    if course:
        return jsonify(course)
    return jsonify({"error": "Course not found"}), 404

# Retrieve all student data for mock login.
@api_bp.route('/students', methods=['GET'])
def get_students():
    all_students = get_student_data()
    return jsonify(all_students)

# In website/routes/api.py

# In website/routes/api.py

# In website/routes/api.py

@api_bp.route('/search', methods=['GET'])
def search_courses():
    # --- Get all parameters from URL ---
    query = request.args.get('q', '')
    term = request.args.get('term', None)
    level = request.args.get('level', None)
    instructor = request.args.get('instructor', None)

    if not query:
        return jsonify({"error": "No query provided"}), 400
        
    query_vector = model.encode(query).tolist()
    
    # --- Build the Pre-Filter ---
    # This filter syntax is NEW and matches the "filter" index type
    filter_conditions = []
    
    if term:
        # 'filter' type uses the 'equals' operator for strings
        filter_conditions.append({
            "equals": {
                "value": term,
                "path": "academic_term"
            }
        })
    
    if level:
        try:
            # 'filter' type also uses 'equals' for numbers
            filter_conditions.append({
                "equals": {
                    "value": int(level),
                    "path": "course_level"
                }
            })
        except ValueError:
            pass # Ignore invalid level

    if instructor:
        # 'filter' type uses 'equals' for strings
        filter_conditions.append({
            "equals": {
                "value": instructor,
                "path": "instructor_name"
            }
        })

    # --- Create the Vector Search Pipeline ---
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_search",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": 10,
                # --- This 'filter' clause is different ---
                "filter": {
                    "compound": {
                        "must": filter_conditions
                    }
                } if filter_conditions else {} # Only add filter if it exists
            }
        },
        {
            "$project": {
                "_id": 0,
                "course_id": 1,
                "score": { "$meta": "vectorSearchScore" }
            }
        }
    ]
    
    # --- The rest of your function (Hydration) is still correct ---
    mongo_results = list(mongo.db.courses.aggregate(pipeline))
    if not mongo_results:
        return jsonify([])

    course_ids = [res['course_id'] for res in mongo_results]
    
    hydrated_results = get_course_details_by_ids_list(course_ids)
    
    score_map = {res['course_id']: res['score'] for res in mongo_results}
    for res in hydrated_results:
        res['score'] = score_map.get(res['course_id'], 0)

    return jsonify(hydrated_results)


# Handle student enrollment in a course.
@api_bp.route('/enroll', methods=['POST'])
def enroll_student():
    data = request.json
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    if not student_id or not course_id:
        return jsonify({"message": "Missing student_id or course_id"}), 400

    try:
        message = enroll_student_in_course(student_id, course_id)
        return jsonify({"message": message}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 409
    
@api_bp.route('/enroll/drop', methods=['POST'])
def drop_enrollment():
    data = request.json or {}
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    if not student_id or not course_id:
        return jsonify({"message": "Missing student_id or course_id"}), 400

    try:
        message = drop_student_enrollment(student_id, course_id)
        return jsonify({"message": message}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 409

    
# Handles: const allUsers = await apiFetch('/api/users');
@api_bp.route('/users', methods=['GET'])
def api_get_users():
    user_data = get_user_data()
    return jsonify(user_data)

# Fetches detailed student data by User ID.
@api_bp.route('/students/<int:user_id>', methods=['GET'])
def api_get_student_details(user_id):
    student_data = get_student_details_by_user_id(user_id)
    if student_data:
        return jsonify(student_data)
    return jsonify({"error": "Student not found"}), 404

# Fetches detailed instructor data by User ID.
@api_bp.route('/instructors/<int:user_id>', methods=['GET'])
def api_get_instructor_details(user_id):
    instructor_data = get_instructor_details_by_user_id(user_id)
    if instructor_data:
        return jsonify(instructor_data)
    return jsonify({"error": "Instructor not found"}), 404

# Retrieves all active enrollments for a specific student.
@api_bp.route('/student/<int:student_id>/enrollments', methods=['GET'])
def api_get_student_enrollments(student_id):
    enrollments = get_student_enrollments(student_id)
    return jsonify(enrollments)

# Fetches all courses taught by a specific instructor ID.
@api_bp.route('/instructor/<int:instructor_id>/courses', methods=['GET'])
def api_get_instructor_courses(instructor_id):
    courses = get_instructor_courses(instructor_id)
    return jsonify(courses)

@api_bp.route('/course/<string:course_id>/students', methods=['GET'])
def api_get_course_students(course_id):
    """Fetches all students enrolled in a specific course ID."""
    students = get_students_in_course(course_id)
    return jsonify(students)
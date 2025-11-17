from flask import Blueprint, request, jsonify
from website import mongo
from sentence_transformers import SentenceTransformer
from ..services.services import (
    get_course_data,
    get_course_details_by_id,
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
    create_course,
    update_course,
    delete_course,
    get_all_users_detailed,
    toggle_user_status,
    create_user,
    update_user,
    delete_user,
    get_user_full_details
)

# Define Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Load the NLP model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# =========================================================
# PUBLIC & STUDENT ROUTES
# =========================================================

@api_bp.route('/courses', methods=['GET'])
def get_courses():
    """Retrieve all course data."""
    all_courses = get_course_data()
    return jsonify(all_courses)

@api_bp.route('/courses/<string:course_id>', methods=['GET'])
def get_course(course_id):
    """Retrieve single course details."""
    course = get_course_details_by_id(course_id)
    if course:
        return jsonify(course)
    return jsonify({"error": "Course not found"}), 404

@api_bp.route('/students', methods=['GET'])
def get_students():
    """Retrieve all student data (for login)."""
    all_students = get_student_data()
    return jsonify(all_students)

@api_bp.route('/search', methods=['GET'])
def search_courses():
    """Semantic Search for courses."""
    # Get parameters safely from query string (args is a dict-like object)
    query = request.args.get('q', '')
    term = request.args.get('term', None)
    level = request.args.get('level', None)
    instructor = request.args.get('instructor', None)

    if not query:
        return jsonify({"error": "No query provided"}), 400
        
    query_vector = model.encode(query).tolist()
    
    # Build Filter
    filter_conditions = []
    if term:
        filter_conditions.append({"equals": {"value": term, "path": "academic_term"}})
    
    if level:
        try:
            filter_conditions.append({"equals": {"value": int(level), "path": "course_level"}})
        except ValueError:
            pass 

    if instructor:
        filter_conditions.append({"equals": {"value": instructor, "path": "instructor_name"}})

    # Vector Search Pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_search",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": 10,
                "filter": {
                    "compound": {
                        "must": filter_conditions
                    }
                } if filter_conditions else {} 
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
    
    mongo_results = list(mongo.db.courses.aggregate(pipeline))
    if not mongo_results:
        return jsonify([])

    # Hydrate results from SQL
    course_ids = [res['course_id'] for res in mongo_results]
    hydrated_results = get_course_details_by_ids_list(course_ids)
    
    # Merge scores
    score_map = {res['course_id']: res['score'] for res in mongo_results}
    for res in hydrated_results:
        res['score'] = score_map.get(res['course_id'], 0)

    return jsonify(hydrated_results)

# =========================================================
# ENROLLMENT ROUTES
# =========================================================

@api_bp.route('/enroll', methods=['POST'])
def enroll_student():
    # Use get_json() to ensure parsing, silent=True returns None on failure
    data = request.get_json(silent=True)
    
    # Validate data is a dictionary
    if data is None or not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON format"}), 400

    # Manual key check instead of .get()
    student_id = data['student_id'] if 'student_id' in data else None
    course_id = data['course_id'] if 'course_id' in data else None

    if not student_id or not course_id:
        return jsonify({"message": "Missing student_id or course_id"}), 400

    try:
        message = enroll_student_in_course(student_id, course_id)
        return jsonify({"message": message}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 409
    except Exception as e:
        return jsonify({"message": "Enrollment failed"}), 500

@api_bp.route('/enroll/drop', methods=['POST'])
def drop_enrollment():
    data = request.get_json(silent=True)

    if data is None or not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON format"}), 400

    # Manual key check
    student_id = data['student_id'] if 'student_id' in data else None
    course_id = data['course_id'] if 'course_id' in data else None

    if not student_id or not course_id:
        return jsonify({"message": "Missing student_id or course_id"}), 400

    try:
        message = drop_student_enrollment(student_id, course_id)
        return jsonify({"message": message}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 409

# =========================================================
# USER INFO ROUTES
# =========================================================

@api_bp.route('/users', methods=['GET'])
def api_get_users():
    user_data = get_user_data()
    return jsonify(user_data)

@api_bp.route('/students/<int:user_id>', methods=['GET'])
def api_get_student_details(user_id):
    student_data = get_student_details_by_user_id(user_id)
    if student_data:
        return jsonify(student_data)
    return jsonify({"error": "Student not found"}), 404

@api_bp.route('/instructors/<int:user_id>', methods=['GET'])
def api_get_instructor_details(user_id):
    instructor_data = get_instructor_details_by_user_id(user_id)
    if instructor_data:
        return jsonify(instructor_data)
    return jsonify({"error": "Instructor not found"}), 404

@api_bp.route('/student/<int:student_id>/enrollments', methods=['GET'])
def api_get_student_enrollments(student_id):
    enrollments = get_student_enrollments(student_id)
    return jsonify(enrollments)

@api_bp.route('/instructor/<int:instructor_id>/courses', methods=['GET'])
def api_get_instructor_courses(instructor_id):
    courses = get_instructor_courses(instructor_id)
    return jsonify(courses)

@api_bp.route('/course/<string:course_id>/students', methods=['GET'])
def api_get_course_students(course_id):
    students = get_students_in_course(course_id)
    return jsonify(students)

# =========================================================
# ADMIN ROUTES
# =========================================================

@api_bp.route('/admin/courses', methods=['POST'])
def api_create_course():
    try:
        # Ensure we have valid JSON dict
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        msg = create_course(data)
        return jsonify({"message": msg}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/admin/courses/<string:course_id>', methods=['PUT'])
def api_update_course(course_id):
    try:
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        msg = update_course(course_id, data)
        return jsonify({"message": msg}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/admin/courses/<string:course_id>', methods=['DELETE'])
def api_delete_course(course_id):
    try:
        msg = delete_course(course_id)
        return jsonify({"message": msg}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@api_bp.route('/admin/users', methods=['GET'])
def api_get_all_users_detailed():
    users = get_all_users_detailed()
    return jsonify(users)

@api_bp.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
def api_toggle_user(user_id):
    try:
        msg = toggle_user_status(user_id)
        return jsonify({"message": msg}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# In website/routes/api.py


# --- ADMIN USER CRUD ROUTES ---

@api_bp.route('/admin/users', methods=['POST'])
def api_create_user():
    print(request.data)
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON"}), 400
        
        msg = create_user(data)
        return jsonify({"message": msg}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/admin/users/<int:user_id>', methods=['GET'])
def api_get_single_user(user_id):
    """Used to populate the Edit Modal"""
    user = get_user_full_details(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@api_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    try:
        data = request.get_json(silent=True)
        msg = update_user(user_id, data)
        return jsonify({"message": msg}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    try:
        msg = delete_user(user_id)
        return jsonify({"message": msg}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
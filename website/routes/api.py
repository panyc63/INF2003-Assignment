from flask import Blueprint, request, jsonify
from website import mongo
import re
import difflib
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
    get_user_full_details,
)

# Define Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Load the NLP model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# SWITCH FROM SQL TO MONGODB OR VICE VERSA
@api_bp.route('/switch-db', methods=['POST'])
def switch_database():
    data = request.get_json(silent=True)
    provider = data.get('provider') # 'sql' or 'mongodb'
    
    from ..services.services import set_db_provider
    set_db_provider(provider)
    
    return jsonify({"message": f"Database switched to {provider}"})

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
    # Get student_id from query params (optional)
    student_id = request.args.get('student_id')
    
    course = get_course_details_by_id(course_id, student_id)
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
    """
    The Ultimate Search Function:
    1. Checks for Exact Code (Regex)
    2. Checks for Typo/Fuzzy Code (Difflib)
    3. Falls back to Semantic Search (Vector) with Filters
    """
    original_query = request.args.get('q', '').strip()
    term = request.args.get('term', None)
    level = request.args.get('level', None)
    instructor = request.args.get('instructor', None)

    if not original_query:
        return jsonify({"error": "No query provided"}), 400

    # Clean up query for code matching (remove spaces)
    clean_query = original_query.replace(" ", "")
    
    # Regex: 1-4 letters, 3-4 numbers (matches "inf1002", "cs101")
    course_id_pattern = re.compile(r'^[a-zA-Z]{1,4}\d{3,4}[a-zA-Z]?$')
    
    # --- STRATEGY 1: CODE LOOKUP ---
    if course_id_pattern.match(clean_query):
        
        # A. Try Exact Match
        exact_matches = list(mongo.db.courses.find(
            {"course_id": {"$regex": f"^{clean_query}$", "$options": "i"}},
            {"_id": 0, "course_id": 1}
        ))
        
        if exact_matches:
            course_ids = [res['course_id'] for res in exact_matches]
            hydrated = get_course_details_by_ids_list(course_ids)
            for res in hydrated: res['score'] = 1.0
            return jsonify(hydrated)
            
        # B. Try Fuzzy Match (Difflib) - The "Typo Fixer"
        # Get ALL real IDs (fast for <1000 items)
        all_courses = list(mongo.db.courses.find({}, {"course_id": 1, "_id": 0}))
        all_ids = [c['course_id'] for c in all_courses]
        
        # Find closest match (must be at least 60% similar)
        closest_matches = difflib.get_close_matches(clean_query.upper(), all_ids, n=1, cutoff=0.6)
        
        if closest_matches:
            best_match = closest_matches[0]
            # Return the corrected course
            hydrated = get_course_details_by_ids_list([best_match])
            for res in hydrated: res['score'] = 0.95 # High score for fuzzy match
            return jsonify(hydrated)

    # --- STRATEGY 2: SEMANTIC VECTOR SEARCH ---
    query_vector = model.encode(original_query).tolist()
    
    # Build Filters using standard MongoDB Operators ($eq)
    filter_list = []
    
    if term:
        filter_list.append({"academic_term": {"$eq": term}})
    
    if level:
        try:
            filter_list.append({"course_level": {"$eq": int(level)}})
        except ValueError:
            pass 

    if instructor:
        filter_list.append({"instructor_name": {"$eq": instructor}})

    # Construct Pipeline
    vector_search_stage = {
        "index": "vector_search",
        "path": "embedding",
        "queryVector": query_vector,
        "numCandidates": 100,
        "limit": 10
    }

    # Only add filter if needed
    if len(filter_list) == 1:
        vector_search_stage["filter"] = filter_list[0]
    elif len(filter_list) > 1:
        vector_search_stage["filter"] = {"$and": filter_list}

    pipeline = [
        {"$vectorSearch": vector_search_stage},
        {"$project": {"_id": 0, "course_id": 1, "score": { "$meta": "vectorSearchScore" }}}
    ]
    
    try:
        mongo_results = list(mongo.db.courses.aggregate(pipeline))
    except Exception as e:
        print(f"Mongo Error: {e}")
        return jsonify({"error": str(e)}), 500

    if not mongo_results:
        return jsonify([])

    # Hydrate Results
    course_ids = [res['course_id'] for res in mongo_results]
    hydrated_results = get_course_details_by_ids_list(course_ids)
    
    # Merge Scores
    score_map = {res['course_id']: res['score'] for res in mongo_results}
    for res in hydrated_results:
        res['score'] = score_map.get(res['course_id'], 0)

    return jsonify(hydrated_results)
    """Semantic Search with Robust Exact Match."""
    original_query = request.args.get('q', '').strip()
    term = request.args.get('term', None)
    level = request.args.get('level', None)
    instructor = request.args.get('instructor', None)

    if not original_query:
        return jsonify({"error": "No query provided"}), 400

    # --- 1. EXACT MATCH CHECK (Regex/Fuzzy) ---
    # (Keep your existing Regex/Fuzzy logic here, it is fine)
    clean_query = original_query.replace(" ", "")
    course_id_pattern = re.compile(r'^[a-zA-Z]{1,4}\d{3,4}[a-zA-Z]?$')
    
    if course_id_pattern.match(clean_query):
        # ... (Keep your exact/fuzzy match logic) ...
        # (If you need me to paste the whole thing again let me know, 
        # but the error is in the vector section below)
        pass 

    # --- 2. SEMANTIC SEARCH (Vector) ---
    query_vector = model.encode(original_query).tolist()
    
    # Build the list of filter conditions
    must_conditions = []
    
    if term:
        # Note: Use 'text' query for string fields in a 'filter' index
        must_conditions.append({
            "text": {
                "query": term,
                "path": "academic_term"
            }
        })
    
    if level:
        try:
            # Note: Use 'equals' for number fields
            must_conditions.append({
                "equals": {
                    "value": int(level),
                    "path": "course_level"
                }
            })
        except ValueError:
            pass 

    if instructor:
        must_conditions.append({
            "text": {
                "query": instructor,
                "path": "instructor_name"
            }
        })

    # --- CONSTRUCT THE PIPELINE ---
    vector_search_stage = {
        "index": "vector_search",
        "path": "embedding",
        "queryVector": query_vector,
        "numCandidates": 100,
        "limit": 10
    }

    # ONLY add the 'filter' field if we actually have conditions
    if must_conditions:
        vector_search_stage["filter"] = {
            "compound": {
                "must": must_conditions
            }
        }

    pipeline = [
        {
            "$vectorSearch": vector_search_stage
        },
        {
            "$project": {
                "_id": 0,
                "course_id": 1,
                "score": { "$meta": "vectorSearchScore" }
            }
        }
    ]
    
    try:
        mongo_results = list(mongo.db.courses.aggregate(pipeline))
    except Exception as e:
        print(f"Mongo Error: {e}")
        return jsonify({"error": "Database search failed"}), 500

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
from flask import Blueprint, request, jsonify
from website import mongo
import re
import difflib
from sentence_transformers import SentenceTransformer
from ..services.services import (
    get_module_data,
    get_module_details_by_id,
    get_student_data,
    get_student_enrollments,
    enroll_student_in_module,
    get_user_data,
    get_student_details_by_user_id,
    get_instructor_details_by_user_id,
    get_instructor_modules,
    get_students_in_module,
    
    drop_student_enrollment_module,
    create_module,
    update_module,
    delete_module,
    get_module_details_by_ids_list,
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

@api_bp.route('/modules', methods=['GET'])
def get_modules():
    """Retrieve all module data."""
    all_modules = get_module_data()
    return jsonify(all_modules)

@api_bp.route('/modules/<string:module_id>', methods=['GET'])
def get_module(module_id):
    # Get student_id from query params (optional)
    student_id = request.args.get('student_id')
    
    module = get_module_details_by_id(module_id, student_id)
    if module:
        return jsonify(module)
    return jsonify({"error": "Module not found"}), 404

@api_bp.route('/students', methods=['GET'])
def get_students():
    """Retrieve all student data (for login)."""
    all_students = get_student_data()
    return jsonify(all_students)
@api_bp.route('/search', methods=['GET'])
def search_modules():
    """Semantic Search for modules with Exact Match fallback."""
    original_query = request.args.get('q', '').strip()
    term = request.args.get('term', None)
    level = request.args.get('level', None)
    instructor = request.args.get('instructor', None)
    
    # Get major param
    student_major = request.args.get('major', None)

    if not original_query:
        return jsonify({"error": "No query provided"}), 400

    # --- 1. EXACT MATCH CHECK (Regex) ---
    clean_query = original_query.replace(" ", "")
    module_code_pattern = re.compile(r'^[a-zA-Z]{1,4}\d{3,4}[a-zA-Z]?$')
    
    if module_code_pattern.match(clean_query):
        # Look in 'modules' collection
        exact_matches = list(mongo.db.modules.find(
            {"module_id": {"$regex": f"^{clean_query}$", "$options": "i"}},
            {"_id": 0, "module_id": 1}
        ))
        
        if exact_matches:
            module_ids = [res['module_id'] for res in exact_matches]
            hydrated_results = get_module_details_by_ids_list(module_ids)
            
            for res in hydrated_results:
                res['score'] = 1.0
                # Ensure module_code exists (it's same as module_id)
                res['module_code'] = res['module_id']
            
            return jsonify(hydrated_results)

    # --- 2. VECTOR SEARCH ---
    query_vector = model.encode(original_query).tolist()
    
    filter_list = []
    
    if term:
        filter_list.append({"academic_term": {"$eq": term}})
    if level:
        try:
            filter_list.append({"module_level": {"$eq": int(level)}})
        except ValueError: pass 
    if instructor:
        filter_list.append({"instructor_name": {"$eq": instructor}})

    # Filter by Major
    if student_major:
        filter_list.append({"target_majors": {"$eq": student_major}})

    vector_search_stage = {
        "index": "vector_index_search",
        "path": "embedding",
        "queryVector": query_vector,
        "numCandidates": 100,
        "limit": 10
    }

    if filter_list:
        vector_filter = filter_list[0] if len(filter_list) == 1 else {"$and": filter_list}
        vector_search_stage["filter"] = vector_filter

    pipeline = [
        {"$vectorSearch": vector_search_stage},
        {"$project": {"_id": 0, "module_id": 1, "score": { "$meta": "vectorSearchScore" }}}
    ]
    
    try:
        mongo_results = list(mongo.db.modules.aggregate(pipeline))
    except Exception as e:
        print(f"Mongo Error: {e}")
        return jsonify({"error": str(e)}), 500

    if not mongo_results:
        return jsonify([])

    module_ids = [res['module_id'] for res in mongo_results]
    hydrated_results = get_module_details_by_ids_list(module_ids)
    
    score_map = {res['module_id']: res['score'] for res in mongo_results}
    
    for res in hydrated_results:
        res['score'] = score_map.get(res['module_id'], 0)
        # Ensure module_code exists
        res['module_code'] = res['module_id']

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
    module_id = data['module_id'] if 'module_id' in data else None

    if not student_id or not module_id:
        return jsonify({"message": "Missing student_id or module_id"}), 400

    try:
        # use module function
        message = enroll_student_in_module(student_id, module_id)
        return jsonify({"message": message}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 409
    except Exception:
        return jsonify({"message": "Enrollment failed"}), 500

@api_bp.route('/enroll/drop', methods=['POST'])
def drop_enrollment():
    data = request.get_json(silent=True)

    if data is None or not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON format"}), 400

    # Manual key check
    student_id = data['student_id'] if 'student_id' in data else None
    module_id = data['module_id'] if 'module_id' in data else None

    if not student_id or not module_id:
        return jsonify({"message": "Missing student_id or module_id"}), 400

    try:
        message = drop_student_enrollment_module(student_id, module_id)
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

@api_bp.route('/instructor/<int:instructor_id>/modules', methods=['GET'])
def api_get_instructor_modules(instructor_id):
    modules = get_instructor_modules(instructor_id)
    return jsonify(modules)

@api_bp.route('/module/<string:module_id>/students', methods=['GET'])
def api_get_module_students(module_id):
    students = get_students_in_module(module_id)
    return jsonify(students)

# =========================================================
# ADMIN ROUTES
# =========================================================

@api_bp.route('/admin/modules', methods=['POST'])
def api_create_module():
    try:
        # Ensure we have valid JSON dict
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        msg = create_module(data)
        return jsonify({"message": msg}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/admin/modules/<string:module_id>', methods=['PUT'])
def api_update_module(module_id):
    try:
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        msg = update_module(module_id, data)
        return jsonify({"message": msg}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/admin/modules/<string:module_id>', methods=['DELETE'])
def api_delete_module(module_id):
    try:
        msg = delete_module(module_id)
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
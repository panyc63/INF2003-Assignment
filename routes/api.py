from flask import Blueprint, request, jsonify
from services import (
    get_course_data,
    semantic_search,
    get_student_data,
    get_student_enrollments,
    enroll_student_in_course,
    get_user_data,
    get_student_details_by_user_id,
    get_instructor_details_by_user_id,
    get_instructor_courses,
    get_students_in_course
)

# Define the Blueprint for the API endpoints with a prefix
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/courses', methods=['GET'])
def get_courses():
    """Retrieve all course data including instructor name and slots remaining."""
    all_courses = get_course_data()
    return jsonify(all_courses)

@api_bp.route('/students', methods=['GET'])
def get_students():
    """Retrieve all student data for mock login."""
    all_students = get_student_data()
    return jsonify(all_students)

@api_bp.route('/search', methods=['POST'])
def search_courses():
    """Handle semantic and keyword-based search queries."""
    data = request.json
    query = data.get('query', '')
    
    results = semantic_search(query)
    
    return jsonify(results)

@api_bp.route('/enroll', methods=['POST'])
def enroll_student():
    """Handle student enrollment in a course."""
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
    
@api_bp.route('/users', methods=['GET'])
def api_get_users():
    """Handles: const allUsers = await apiFetch('/api/users');"""
    user_data = get_user_data()
    return jsonify(user_data)

@api_bp.route('/students/<int:user_id>', methods=['GET'])
def api_get_student_details(user_id):
    """Fetches detailed student data by User ID."""
    student_data = get_student_details_by_user_id(user_id)
    if student_data:
        return jsonify(student_data)
    return jsonify({"error": "Student not found"}), 404

@api_bp.route('/instructors/<int:user_id>', methods=['GET'])
def api_get_instructor_details(user_id):
    """Fetches detailed instructor data by User ID."""
    instructor_data = get_instructor_details_by_user_id(user_id)
    if instructor_data:
        return jsonify(instructor_data)
    return jsonify({"error": "Instructor not found"}), 404

@api_bp.route('/student/<int:student_id>/enrollments', methods=['GET'])
def api_get_student_enrollments(student_id):
    """Retrieves all active enrollments for a specific student."""
    enrollments = get_student_enrollments(student_id)
    return jsonify(enrollments)

@api_bp.route('/instructor/<int:instructor_id>/courses', methods=['GET'])
def api_get_instructor_courses(instructor_id):
    """Fetches all courses taught by a specific instructor ID."""
    courses = get_instructor_courses(instructor_id)
    return jsonify(courses)

@api_bp.route('/course/<string:course_id>/students', methods=['GET'])
def api_get_course_students(course_id):
    """Fetches all students enrolled in a specific course ID."""
    students = get_students_in_course(course_id)
    return jsonify(students)
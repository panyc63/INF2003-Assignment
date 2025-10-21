import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
# Note: Assuming your other files are named models.py and services.py in the same folder
from models import db, Course, Instructor, Student, Enrollment
from services import initialize_database, get_course_data, get_student_data, get_instructor_data, simulate_semantic_search, enroll_student_in_course

# Initialize Flask app
# Template folder remains 'website'
app = Flask(__name__, template_folder='website', static_folder='website/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ucms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key' # Needed for session management

# Initialize database integration
db.init_app(app)

# --- ROUTES ---

@app.route('/')
def home():
    """Renders the Home page."""
    return render_template('home.html', view='home')

@app.route('/about')
def about():
    """Renders the About Us page."""
    return render_template('about.html', view='about')

@app.route('/course')
def course():
    """Renders the Course page."""
    return render_template('course.html', view='course')
@app.route('/detail')
def detail():
    """Renders the Details page."""
    return render_template('detail.html', view='detail')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Renders the Login page and handles login form submission."""

    if request.method == 'POST':
        # This part is mostly for show, the actual state change is client-side in the SPA logic
        return redirect(url_for('dashboard'))

    return render_template('login.html', view='login')

@app.route('/dashboard')
def dashboard():
    """Renders the Dashboard page."""
    # Note: We rely on client-side JS to check the loggedIn state after rendering this template
    return render_template('dashboard.html', view='dashboard')

# --- API ENDPOINTS (Remain the same) ---

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Retrieve all course data including instructor name and slots remaining."""
    all_courses = get_course_data()
    return jsonify(all_courses)

@app.route('/api/students', methods=['GET'])
def get_students():
    """Retrieve all student data for mock login."""
    all_students = get_student_data()
    return jsonify(all_students)

@app.route('/api/search', methods=['POST'])
def search_courses():
    """Handle semantic and keyword-based search queries."""
    data = request.json
    query = data.get('query', '')
    
    results = simulate_semantic_search(query)
    
    return jsonify(results)

@app.route('/api/enroll', methods=['POST'])
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
        return jsonify({"message": str(e)}), 409 # Conflict

@app.route('/api/student/<int:student_id>/enrollments', methods=['GET'])
def get_student_enrollments(student_id):
    """Retrieve all courses a specific student is enrolled in."""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404

    enrolled_courses = [
        {
            "course_id": e.course.id,
            "title": e.course.title,
            "instructor_name": e.course.instructor.name if e.course.instructor else "TBA",
            "credits": e.course.credits
        }
        for e in student.enrollments
    ]
    return jsonify(enrolled_courses)


if __name__ == '__main__':
    # Database initialization runs explicitly within the app context
    with app.app_context():
        db.create_all()
        initialize_database()
        
    # Run the application
    app.run(debug=True, port=5000)
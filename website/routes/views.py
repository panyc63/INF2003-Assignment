from flask import Blueprint, render_template

# Define Blueprint
views_bp = Blueprint('views', __name__)

# =========================================================
# PUBLIC PAGES
# =========================================================

@views_bp.route('/')
def home():
    """Renders the landing page."""
    return render_template('home.html', view='home')

@views_bp.route('/about')
def about():
    """Renders the About Us page."""
    return render_template('about.html', view='about')

@views_bp.route('/courses')
def courses():
    """Renders the public Course Catalog page."""
    return render_template('course.html', view='courses')

@views_bp.route('/course/<string:course_id>')
def course_detail(course_id):
    """
    Renders the specific Course Details page.
    We pass course_id to the template so the JS can query the API.
    """
    return render_template('course_detail.html', course_id=course_id, view='course_detail')

# =========================================================
# AUTHENTICATION
# =========================================================

@views_bp.route('/login')
def login():
    """Renders the Login page."""
    # Note: Actual login logic is handled by JS/API
    return render_template('login.html', view='login')

# =========================================================
# STUDENT VIEWS
# =========================================================

@views_bp.route('/dashboard')
def dashboard():
    """Renders the Student Dashboard."""
    return render_template('dashboard.html', view='dashboard')

# =========================================================
# INSTRUCTOR VIEWS
# =========================================================

@views_bp.route('/instructor_dashboard')
def instructor_dashboard():
    """Renders the Instructor Dashboard."""
    return render_template('instructor_dashboard.html', view='instructor_dashboard')

# =========================================================
# ADMIN VIEWS (NEW)
# =========================================================

@views_bp.route('/admin_dashboard')
def admin_dashboard():
    """Renders the main Admin Dashboard."""
    return render_template('admin_dashboard.html', view='admin_dashboard')

@views_bp.route('/admin/courses')
def admin_courses():
    """Renders the Admin Course Management page."""
    return render_template('admin_courses.html', view='admin_courses')

@views_bp.route('/admin/users')
def admin_users():
    """Renders the Admin User Management page."""
    return render_template('admin_users.html', view='admin_users')
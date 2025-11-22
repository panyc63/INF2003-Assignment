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

@views_bp.route('/modules')
def modules():
    """Renders the public Module Catalog page."""
    return render_template('module.html', view='modules')

@views_bp.route('/module/<string:module_id>')
def module_detail(module_id):
    """
    Renders the specific Module Details page.
    We pass module_id to the template so the JS can query the API.
    """
    return render_template('module_detail.html', module_id=module_id, view='module_detail')

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

@views_bp.route('/admin/modules')
def admin_modules():
    """Renders the Admin Module Management page."""
    return render_template('admin_modules.html', view='admin_modules')

@views_bp.route('/admin/users')
def admin_users():
    """Renders the Admin User Management page."""
    return render_template('admin_users.html', view='admin_users')
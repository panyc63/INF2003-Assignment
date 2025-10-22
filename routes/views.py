from flask import Blueprint, render_template, request, redirect, url_for

#redirect blueprint
views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def home():
    """Renders the Home page."""
    return render_template('home.html', view='home')

@views_bp.route('/about')
def about():
    """Renders the About Us page."""
    return render_template('about.html', view='about')

@views_bp.route('/course')
def course():
    """Renders the Course page."""
    return render_template('course.html', view='course')

@views_bp.route('/detail')
def detail():
    """Renders the Details page."""
    return render_template('detail.html', view='detail')

@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('views.dashboard'))

    return render_template('login.html', view='login')

@views_bp.route('/dashboard')
def dashboard():
    """Renders the Student Dashboard page."""
    return render_template('dashboard.html', view='dashboard')

@views_bp.route('/instructor_dashboard')
def instructor_dashboard():
    """Renders the Instructor Dashboard page."""
    return render_template('instructor_dashboard.html', view='instructor_dashboard')
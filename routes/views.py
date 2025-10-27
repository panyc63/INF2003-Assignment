from flask import Blueprint, render_template, request, redirect, url_for

#redirect blueprint
views_bp = Blueprint('views', __name__)

# Renders the Home page.
@views_bp.route('/')
def home():
    return render_template('home.html', view='home')

# Renders the About Us page.
@views_bp.route('/about')
def about():
    return render_template('about.html', view='about')

# Renders the Course page.
@views_bp.route('/course')
def course():
    return render_template('course.html', view='course')

# Renders the Course Detail page.
@views_bp.route('/course-detail/<string:course_id>')
def course_detail(course_id):
    # Just pass the ID directly to the template.
    # The template's JavaScript will use this ID to fetch data.
    return render_template(
        'course_detail.html', 
        course_id=course_id, 
        view='course_detail'
    )

# Renders the Details page.
@views_bp.route('/detail')
def detail():
    return render_template('detail.html', view='detail')

# Renders the Login page
@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('views.dashboard'))

    return render_template('login.html', view='login')

# Renders the Student Dashboard page.
@views_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', view='dashboard')

# Renders the Instructor Dashboard page.
@views_bp.route('/instructor_dashboard')
def instructor_dashboard():
    return render_template('instructor_dashboard.html', view='instructor_dashboard')
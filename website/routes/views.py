from flask import Blueprint, render_template, request, redirect, url_for
from ..services.services import get_course_data,get_course_details_by_id

#redirect blueprint
views_bp = Blueprint('views', __name__)


# Renders the Home page.
@views_bp.route('/')
def home():
    all_courses = get_course_data()
    return render_template('home.html', courses=all_courses, view='home')

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
    all_courses = get_course_data()
    return render_template('course.html', courses=all_courses, view='course')

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


@views_bp.route('/course/<string:course_id>')
def course_info(course_id):
    selected_course = get_course_details_by_id(course_id)
    if selected_course is None:
        return render_template('404.html', message=f"Course ID {course_id} not found"), 404
        
    return render_template('course_info.html', course=selected_course, view='course')
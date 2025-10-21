from models import db, Course, Instructor, Student, Enrollment
from sqlalchemy.exc import IntegrityError
from flask import current_app

# --- Mock Data ---

MOCK_INSTRUCTORS = [
    {"id": 1, "name": "Dr. Alan Turing", "department": "Computer Science"},
    {"id": 2, "name": "Prof. Ada Lovelace", "department": "Engineering"},
    {"id": 3, "name": "Dr. Grace Hopper", "department": "Mathematics"}
]

MOCK_COURSES = [
    {"id": "CS101", "title": "Fundamentals of Programming (FOP)", "description": "Introduction to Python and core programming concepts. This is a foundational course for all majors.", "prerequisites": "None", "credits": 4, "department": "CS", "max_intake": 10, "instructor_id": 1},
    {"id": "CS205", "title": "Database Systems", "description": "Relational algebra, SQL, and database design. Core class for IT specialization.", "prerequisites": "CS101", "credits": 4, "department": "CS", "max_intake": 5, "instructor_id": 1},
    {"id": "ENG101", "title": "Circuit Analysis", "description": "Basic electric circuits, Ohm's law, and network theorems.", "prerequisites": "High School Physics", "credits": 3, "department": "Engineering", "max_intake": 15, "instructor_id": 2},
    {"id": "MATH301", "title": "Advanced Calculus", "description": "Differential equations and multivariate calculus. Essential for engineering and physics.", "prerequisites": "MATH101", "credits": 4, "department": "Mathematics", "max_intake": 10, "instructor_id": 3},
    {"id": "CS400", "title": "Artificial Intelligence Concepts", "description": "A postgraduate level course exploring machine learning, neural networks, and AI ethics. Required core class for M.S. students.", "prerequisites": "CS205", "credits": 4, "department": "CS", "max_intake": 8, "instructor_id": 3},
]

MOCK_STUDENTS = [
    {"id": 1001, "student_id_num": "S1001A", "name": "Elara Vance", "academic_history": "[]"},
    {"id": 1002, "student_id_num": "S1002B", "name": "Kaelen Rix", "academic_history": "[]"},
    {"id": 1003, "student_id_num": "S1003C", "name": "Jax Teller", "academic_history": "[]"},
]

# --- Simulated Semantic Search Component ---
# In a real app, this would use BERT embeddings and a vector DB (like Chroma or FAISS).

# Custom Ontology/Synonym Map for highly specific terms
ONTOLOGY_MAP = {
    "fop": "Fundamentals of Programming",
    "core class": "required course",
    "required": "core class",
    "database": "database systems",
    "ai": "artificial intelligence concepts",
    "next trimester": "current offerings", # Mocking current semester
    "alan": "dr. alan turing",
    "ada": "prof. ada lovelace",
    "grace": "dr. grace hopper",
}

def simulate_semantic_search(query):
    """
    Simulates semantic search by performing a broad keyword/ontology-based match
    against course titles, descriptions, and instructor names.
    """
    query_lower = query.lower()
    
    for key, value in ONTOLOGY_MAP.items():
        if key in query_lower:
            query_lower += f" {value.lower()}"

    search_terms = query_lower.split()
    results = []
    
    all_courses = Course.query.all()
    
    for course in all_courses:
        instructor_name = course.instructor.name.lower() if course.instructor else ""
        course_text = f"{course.id} {course.title} {course.description} {course.department} {instructor_name}".lower()
        
        score = 0
        for term in search_terms:
            if len(term) > 2 and term in course_text:
                score += 1

        if score > 0:
            slots_left = course.slots_available()
            results.append({
                "course_id": course.id,
                "title": course.title,
                "description": course.description,
                "prerequisites": course.prerequisites,
                "credits": course.credits,
                "department": course.department,
                "instructor_name": course.instructor.name if course.instructor else "TBA",
                "slots_left": slots_left,
                "relevance_score": score # Used for sorting/ranking
            })

    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results



def initialize_database():
    """Populates the database with mock data if tables are empty."""
    if Course.query.count() == 0:
        for data in MOCK_INSTRUCTORS:
            db.session.add(Instructor(**data))
        
        for data in MOCK_COURSES:
            db.session.add(Course(**data))

        for data in MOCK_STUDENTS:
            db.session.add(Student(**data))

        db.session.commit()

        # Enroll one student in one course for demo purposes
        s1 = Student.query.get(1001)
        c1 = Course.query.get("CS101")
        if s1 and c1:
            enrollment = Enrollment(student=s1, course=c1)
            db.session.add(enrollment)
            db.session.commit()


def get_course_data():
    """Fetches all courses with calculated slots and instructor names."""
    courses = Course.query.all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "prerequisites": c.prerequisites,
            "credits": c.credits,
            "department": c.department,
            "max_intake": c.max_intake,
            "slots_left": c.slots_available(),
            "instructor_name": c.instructor.name if c.instructor else "TBA"
        }
        for c in courses
    ]

def get_student_data():
    """Fetches all students."""
    students = Student.query.all()
    return [{"id": s.id, "name": s.name, "student_id_num": s.student_id_num} for s in students]

def get_instructor_data():
    """Fetches all instructors."""
    instructors = Instructor.query.all()
    return [{"id": i.id, "name": i.name, "department": i.department} for i in instructors]


def enroll_student_in_course(student_id, course_id):
    """Handles the enrollment transaction with slot checking."""
    student = Student.query.get(student_id)
    course = Course.query.get(course_id)

    if not student:
        raise ValueError("Student not found.")
    if not course:
        raise ValueError("Course not found.")

    if course.slots_available() <= 0:
        raise ValueError("Course is full. Enrollment failed.")
    
    # Check if student is already enrolled
    existing_enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing_enrollment:
        raise ValueError("Student is already enrolled in this course.")

    try:
        new_enrollment = Enrollment(student=student, course=course)
        db.session.add(new_enrollment)
        db.session.commit()
        return f"Successfully enrolled {student.name} in {course.id} - {course.title}."
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Database error occurred during enrollment.")
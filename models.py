from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for the M:M relationship between Student and Course
class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    
    # Relationships for easy access
    student = db.relationship("Student", back_populates="enrollments")
    course = db.relationship("Course", back_populates="enrollments")

class Instructor(db.Model):
    __tablename__ = 'instructors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50))

    # One-to-many relationship with Course
    courses_taught = db.relationship("Course", back_populates="instructor", lazy='dynamic')

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.String(10), primary_key=True) # e.g., 'CS101'
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    prerequisites = db.Column(db.String(250))
    credits = db.Column(db.Float)
    department = db.Column(db.String(50))
    max_intake = db.Column(db.Integer, default=30) # Total slots available
    
    # Foreign key relationship to Instructor
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'), nullable=True)

    # Relationships
    instructor = db.relationship("Instructor", back_populates="courses_taught")
    enrollments = db.relationship("Enrollment", back_populates="course", lazy='dynamic', cascade="all, delete-orphan")

    def slots_available(self):
        """Calculates available enrollment slots."""
        return self.max_intake - self.enrollments.count()

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id_num = db.Column(db.String(20), unique=True, nullable=False) # e.g., 'S1234567A'
    name = db.Column(db.String(100), nullable=False)
    academic_history = db.Column(db.Text) # Storing previous courses as text/JSON string

    # Many-to-many relationship with Course via Enrollment
    enrollments = db.relationship("Enrollment", back_populates="student", lazy='dynamic', cascade="all, delete-orphan")
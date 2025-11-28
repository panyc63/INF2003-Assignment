from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Base table for all system users (students, instructors, admins).
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True) 
    university_id = db.Column(db.String(50), unique=True, nullable=True, index=True) 
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False) 
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    student = db.relationship("Student", uselist=False, back_populates="user")
    instructor = db.relationship("Instructor", uselist=False, back_populates="user")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

# Holds details specific to student users, linked one-to-one with the User table.
class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    enrollment_year = db.Column(db.Integer, nullable=False)
    major = db.Column(db.String(50))
    expected_graduation = db.Column(db.String(10)) 
    gpa = db.Column(db.Numeric(3, 2)) 
    current_standing = db.Column(db.String(20))

    user = db.relationship("User", back_populates="student")
    enrollments = db.relationship("Enrollment", back_populates="student", lazy='dynamic', cascade="all, delete-orphan")
    submissions = db.relationship("Submission", back_populates="student", lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student ID:{self.student_id} Major:{self.major}>"

# Holds details specific to instructor users, linked one-to-one with the User table.
class Instructor(db.Model):
    __tablename__ = 'instructors'
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    department_code = db.Column(db.String(10), nullable=True)
    office_location = db.Column(db.String(50))
    office_hours = db.Column(db.Text)
    title = db.Column(db.String(50))

    user = db.relationship("User", back_populates="instructor")
    modules_taught = db.relationship("Module", back_populates="instructor", lazy='dynamic')

    def __repr__(self):
        return f"<Instructor ID:{self.instructor_id} Title:{self.title}>"

# Defines the structure and details of a university course.
class Module(db.Model):
    __tablename__ = 'modules'
    module_id = db.Column(db.String(10), primary_key=True)
    module_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer)
    academic_term = db.Column(db.String(20))
    max_capacity = db.Column(db.Integer, default=30)
    current_enrollment = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    target_majors = db.Column(db.String(100))  # New field for target majors

    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.instructor_id'), nullable=True)

    instructor = db.relationship("Instructor", back_populates="modules_taught")
    enrollments = db.relationship("Enrollment", back_populates="module", lazy='dynamic', cascade="all, delete-orphan")
    assignments = db.relationship("Assignment", back_populates="module", lazy='dynamic', cascade="all, delete-orphan")

    prerequisites = db.relationship("Prerequisites", foreign_keys='Prerequisites.module_id', back_populates="module", lazy='dynamic', cascade="all, delete-orphan")
    is_prerequisite_for = db.relationship("Prerequisites", foreign_keys='Prerequisites.requires_module_id', back_populates="prerequisite_module", lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Module {self.module_id}: {self.module_name}>"


# Defines the many-to-many relationship for module prerequisites.
class Prerequisites(db.Model):
    __tablename__ = 'prerequisites'
    module_id = db.Column(db.String(10), db.ForeignKey('modules.module_id'), primary_key=True)
    requires_module_id = db.Column(db.String(10), db.ForeignKey('modules.module_id'), primary_key=True)

    module = db.relationship("Module", foreign_keys=[module_id], back_populates="prerequisites")
    prerequisite_module = db.relationship("Module", foreign_keys=[requires_module_id], back_populates="is_prerequisite_for")

    def __repr__(self):
        return f"<Prerequisite: {self.module_id} requires {self.requires_module_id}>"

# Represents a student's enrollment in a specific course.
class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), primary_key=True)
    module_id = db.Column(db.String(10), db.ForeignKey('modules.module_id'), primary_key=True)
    
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow) 
    final_grade = db.Column(db.String(2)) 
    status = db.Column(db.String(20), default='Enrolled')
    student = db.relationship("Student", back_populates="enrollments")
    module = db.relationship("Module", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment student={self.student_id} module={self.module_id}>"

# Defines a single assignment belonging to a course.
class Assignment(db.Model):
    __tablename__ = 'assignments'
    assignment_id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.String(10), db.ForeignKey('modules.module_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    assignment_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    module = db.relationship("Module", back_populates="assignments")
    submissions = db.relationship("Submission", back_populates="assignment", lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Assignment {self.assignment_id}: {self.title}>"

# Records a student's submission for a specific assignment.
class Submission(db.Model):
    __tablename__ = 'submissions'
    submission_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.assignment_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(255))
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    status = db.Column(db.String(20))

    assignment = db.relationship("Assignment", back_populates="submissions")
    student = db.relationship("Student", back_populates="submissions")

    def __repr__(self):
        return f"<Submission {self.submission_id} by student {self.student_id}>"
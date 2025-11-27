from user import User
from datetime import datetime

class Student(User):
    student_id: int
    enrollment_year: int
    major: str
    expected_graduation: str
    gpa: float
    current_standing: str
    major_id: str

    def __init__(self, user_id: int, university_id: str, email: str, password_hash: str, first_name: str, last_name: str,
                 role: str, date_joined: datetime, last_login: datetime, is_active: bool, student_id: int, enrollment_year: int,
                 major: str, expected_graduation: str, gpa: float, current_standing: str, major_id: str):
        super().__init__(user_id, university_id, email, password_hash, first_name, last_name, role, date_joined,
                         last_login, is_active)
        self.student_id = student_id
        self.enrollment_year = enrollment_year
        self.major = major
        self.expected_graduation = expected_graduation
        self.gpa = gpa
        self.current_standing = current_standing
        self.major_id = major_id
from user import User
from datetime import datetime

class Instructor(User):
    instructor_id: int
    department_code: str
    office_location: str
    office_hours: str
    title: str

    def __init__(self, user_id: int, university_id: str, email: str, password_hash: str, first_name: str, last_name: str,
                 role: str, date_joined: datetime, last_login: datetime, is_active: bool, instructor_id: int,
                 department_code: str, office_location: str, office_hours: str, title: str):
        super().__init__(user_id, university_id, email, password_hash, first_name, last_name, role, date_joined,
                         last_login, is_active)
        self.instructor_id = instructor_id
        self.department_code = department_code
        self.office_location = office_location
        self.office_hours = office_hours
        self.title = title
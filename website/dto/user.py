from typing import Optional

class UserBasicDTO:
    user_id: int
    email: str
    name: str
    role: str

    def __init__(self, user_id: int, email: str, first_name: str, last_name: str, role: str):
        self.user_id = user_id
        self.email = email
        self.name = first_name + " " + last_name
        self.role = role

class UserDetailedDTO:
    user_id: int
    university_id: str
    name: str
    email: str
    details: str

    def __init__(self, user_id: int, university_id: str, first_name: str, last_name, email: str, details: str):
        self.user_id = user_id
        self.university_id = university_id
        self.name = first_name + " " + last_name
        self.email = email
        self.details = details

class UserFullDetailsDTO:
    user_id: int
    university_id: str
    first_name: str
    last_name: str
    email: str
    role: str
    major: str
    enrollment_year: int
    department_code: str
    title: str

    def __init__(self, user_id: int, university_id: str, first_name: str, last_name: str, email: str, role: str,
                 major: str, enrollment_year: int, department_code: str, title: str):
        self.user_id = user_id
        self.university_id = university_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = role
        self.major = major
        self.enrollment_year = enrollment_year
        self.department_code = department_code
        self.title = title

class UserInsertDTO:
    university_id: str
    email: str
    password_hash: str
    first_name: str
    last_name: str
    role: str

    def __init__(self, university_id: str, email: str, password_hash: str, first_name: str, last_name: str, role: str):
        self.university_id = university_id
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

class UserStudentInsertDTO:
    student_id: int
    major: str
    enrollment_year: int

    def __init__(self, student_id: int, major: str, enrollment_year: int):
        self.student_id = student_id
        self.major = major
        self.enrollment_year = enrollment_year

class UserInstructorInsertDTO:
    instructor_id: int
    department_code: str
    title: str

    def __init__(self, instructor_id: int, department_code: str, title: str):
        self.instructor_id = instructor_id
        self.department_code = department_code
        self.title = title

class UserUpdateDTO:
    first_name: str
    last_name: str
    email: str

    def __init__(self, first_name: str, last_name: str, email: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
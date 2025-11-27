import datetime

class User:
    user_id: int
    university_id: str
    email: str
    password_hash: str
    first_name: str
    last_name: str
    role: str
    date_joined: datetime.datetime
    last_login: datetime.datetime
    is_active: bool

    def __init__(self, user_id: int, university_id: str, email: str, password_hash: str, first_name: str,
                 last_name: str, role: str, date_joined: datetime.datetime, last_login: datetime.datetime, is_active: bool):
        self.user_id = user_id
        self.university_id = university_id
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.date_joined = date_joined
        self.last_login = last_login
        self.is_active = is_active

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

    def __init__(self, user_id: int, university_id: str, first_name: str, last_name: str, email: str, role: str):
        self.user_id = user_id
        self.university_id = university_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = role

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

class UserUpdateDTO:
    first_name: str
    last_name: str
    email: str

    def __init__(self, first_name: str, last_name: str, email: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
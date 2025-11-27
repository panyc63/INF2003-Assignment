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
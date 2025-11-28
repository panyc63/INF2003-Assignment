from sqlalchemy import TextClause, text, Row
from typing import Sequence, Union
from ... import db
from ...dto.user import UserInsertDTO, UserBasicDTO , UserDetailedDTO, UserInstructorInsertDTO, UserStudentInsertDTO, UserUpdateDTO, UserFullDetailsDTO

def get_user_data() -> list[UserBasicDTO]:
    sql_statement: TextClause = text("SELECT user_id, email, first_name, last_name, role FROM users")
    rows: Sequence[Row] = db.session.execute(sql_statement).all()

    return [UserBasicDTO(r.user_id, r.email, r.first_name, r.last_name, r.role) for r in rows]

def get_all_users_detailed() -> list[UserDetailedDTO]:
    sql_statement: TextClause = text("""SELECT u.user_id, u.university_id, u.first_name, u.last_name, u.email, u.role,
                                            u.is_active, s.major, i.department_code
                                        FROM users u
                                        LEFT JOIN students s ON u.user_id = s.student_id
                                        LEFT JOIN instructors i ON u.user_id = i.instructor_id
                                        ORDER BY u.date_joined DESC)""")
    rows: Sequence[Row] = db.session.execute(sql_statement).all()

    return [UserDetailedDTO(r.user_id, r.university_id, r.first_name, r.last_name, r.email,
                            r.major if r.role == 'student' else (r.department_code if r.role == 'instructor' else 'Admin'))
                            for r in rows]

def create_user(user: UserInsertDTO) -> int:
    try:
        sql_statement: TextClause = text("""INSERT INTO users (university_id, email, password_hash, first_name,
                                         last_name, role, is_active) VALUES (:uid, :email, 'pass', :fname, :lname, :role, 1)""")
        result = db.session.execute(sql_statement, {
            "uid": user.university_id, "email": user.email, "fname": user.first_name,
            "lname": user.last_name, "role": user.role
        })

        return result.lastrowid
    except Exception as e:
        raise e
    
def create_student(student: UserStudentInsertDTO) -> int:
    try:
        sql_statement: TextClause = text("""INSERT INTO students (student_id, major, enrollment_year) VALUES (:id, :major, :year)""")
        result = db.session.execute(sql_statement, {"id": student.student_id, "major": student.major, "year": student.enrollment_year})

        return result.lastrowid
    except Exception as e:
        raise e
    
def create_instructor(instructor: UserInstructorInsertDTO) -> int:
    try:
        sql_statement: TextClause = text("""INSERT INTO instructors (instructor_id, department_code, title)
                                         VALUES (:id, :dept, :title)""")
        result = db.session.execute(sql_statement, {"id": instructor.instructor_id, "dept": instructor.department_code,
                                                     "title": instructor.title})

        return result.lastrowid
    except Exception as e:
        raise e
    
def update_user(user_id: int, user: UserUpdateDTO) -> int:
    sql_statement: TextClause = text("UPDATE users SET first_name=:fname, last_name=:lname, email=:email WHERE user_id=:id")
    result = db.session.execute(sql_statement, {"fname": user.first_name, "lname": user.last_name, "email": user.email,
                                                "id": user_id})
    
    return result.rowcount if result.rowcount > 0 else -1

def delete_user(user_id: int) -> int:
    sql_statement: TextClause = text("DELETE FROM users WHERE user_id=:id")
    result = db.session.execute(sql_statement, {"id": user_id})

    return result.rowcount if result.rowcount > 0 else -1

def toggle_user_status(user_id: int) -> int:
    sql_statement: TextClause = text("UPDATE users SET is_active = NOT is_active WHERE user_id=:id")
    result = db.session.execute(sql_statement, {"id": user_id})

    return result.rowcount if result.rowcount > 0 else -1

def get_user_full_details(user_id: int) -> Union[UserFullDetailsDTO, None]:
    sql_statement = text("""SELECT u.*, s.major, s.enrollment_year, i.department_code, i.title FROM users u
                         LEFT JOIN students s ON u.user_id = s.student_id
                         LEFT JOIN instructors i ON u.user_id = i.instructor_id
                         WHERE u.user_id = :id""")
    row = db.session.execute(sql_statement, {"id": user_id}).first()

    if row:
        return UserFullDetailsDTO(row.user_id, row.university_id, row.first_name, row.last_name, row.email, row.role,
                                  row.major, row.enrollment_year, row.department_code, row.title)
    else:
        return None
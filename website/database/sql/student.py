from sqlalchemy import TextClause, text, Row
from typing import Sequence, Union
from ... import db
from ...dto.student import StudentEnrollmentDTO, StudentBasicDTO, StudentDetailsByUserIdDTO

def enroll_student_in_module(student_id: int, module_id: int) -> bool:
    try:
        sql_statement: TextClause = text("SELECT 1 FROM enrollments WHERE student_id=:sid AND module_id=:cid")
        result = db.session.execute(sql_statement, {"sid": student_id, "cid": module_id}).first()

        if result:
            raise ValueError("Already enrolled")
        
        sql_statement = text("INSERT INTO enrollments (student_id, module_id, status) VALUES (:sid, :cid, 'Enrolled')")
        db.session.execute(sql_statement, {"sid":student_id, "cid":module_id})

        sql_statement = text("UPDATE modules SET current_enrollment = current_enrollment + 1 WHERE module_id=:cid")
        db.session.execute(sql_statement, {"cid": module_id})
        return True
    except Exception as e:
        raise e
    
def drop_student_enrollment_module(student_id: int, module_id: int) -> bool:
    has_update: bool = True

    sql_statement: TextClause = text("DELETE FROM enrollments WHERE student_id=:sid AND module_id=:cid")
    result = db.session.execute(sql_statement, {"sid":student_id, "cid":module_id})
    if result.rowcount == 0:
        has_update = False

    sql_statement = text("UPDATE modules SET current_enrollment = current_enrollment - 1 WHERE module_id=:cid")
    result = db.session.execute(sql_statement, {"cid": module_id})
    if result.rowcount == 0:
        has_update = False

    return has_update

def get_student_enrollments(student_id) -> list[StudentEnrollmentDTO]:
    sql_statement: TextClause = text("""SELECT e.module_id, c.module_name, c.credits, c.academic_term, e.status, 
                                        e.final_grade, u.first_name, u.last_name
                                     FROM enrollments e
                                     JOIN modules c ON e.module_id = c.module_id
                                     LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
                                     LEFT JOIN users u ON i.instructor_id = u.user_id
                                     WHERE e.student_id = :sid""")
    
    result: Sequence[Row] = db.session.execute(sql_statement, {"sid": student_id}).all()
    
    return [StudentEnrollmentDTO(r.module_id, r.module_name, r.credits, r.academic_term, r.status, r.final_grade,
                                 f"{r.first_name} {r.last_name}" if r.first_name else "TBA")
                                 for r in result]

def get_student_data() -> list[StudentBasicDTO]:
    sql_statement: TextClause = text("""SELECT s.student_id, u.university_id, u.first_name, u.last_name, s.major 
                                     FROM students s 
                                     JOIN users u ON s.student_id = u.user_id""")
    result: Sequence[Row] = db.session.execute(sql_statement).all()

    return [StudentBasicDTO(r.student_id, r.university_id, f"{r.first_name} {r.last_name}", r.major) for r in result]

def get_student_details_by_user_id(user_id) -> Union[StudentDetailsByUserIdDTO, None]:
    sql_statement: TextClause = text("SELECT student_id, enrollment_year, major, major_id FROM students WHERE student_id = :uid")
    result = db.session.execute(sql_statement, {"uid": user_id}).first()
    
    if result:
        return StudentDetailsByUserIdDTO(result.student_id, result.enrollment_year, result.major, result.major_id)
    else: 
        return None
    
def get_students_in_module(cid) -> list[StudentBasicDTO]:
    sql_statement: TextClause = text("""SELECT s.student_id, u.first_name, u.last_name, s.major, u.university_id 
                                     FROM students s 
                                     JOIN enrollments e ON s.student_id=e.student_id JOIN users u ON s.student_id=u.user_id WHERE e.module_id=:cid""")
    result: Sequence[Row] = db.session.execute(sql_statement, {"cid": cid}).all()

    return [StudentBasicDTO(r.student_id, r.university_id, f"{r.first_name} {r.last_name}", r.major) for r in result]
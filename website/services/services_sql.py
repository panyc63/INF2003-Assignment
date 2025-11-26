from .. import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from typing import Dict, Any, List

# =====================================================
#  SQL READ OPERATIONS
# =====================================================

def get_module_data():
    sql = text("""
        SELECT 
            c.*, 
            u.first_name AS instructor_first, 
            u.last_name AS instructor_last,
            (SELECT GROUP_CONCAT(pr.requires_module_id SEPARATOR ', ') 
             FROM prerequisites pr 
             WHERE pr.module_id = c.module_id) AS prereqs_list
        FROM modules c
        LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
        LEFT JOIN users u ON i.instructor_id = u.user_id
    """)
    modules = db.session.execute(sql).all()
    
    results = []
    for c in modules:
        instructor_name = f"{c.instructor_first} {c.instructor_last}" if c.instructor_first else "TBA"
        prereqs = c.prereqs_list.split(',') if c.prereqs_list else []

        results.append({
            "module_id": c.module_id,
            "module_code": c.module_code if hasattr(c, 'module_code') else None,
            "module_name": c.module_name,
            "description": c.description,
            "prerequisites": ", ".join(prereqs) if prereqs else "None",
            "credits": c.credits,
            "academic_term": c.academic_term,
            "max_capacity": c.max_capacity,
            "current_enrollment": c.current_enrollment,
            "slots_left": c.max_capacity - (c.current_enrollment or 0),
            "instructor_name": instructor_name,
            "created_at": c.created_at.isoformat() if c.created_at else None
        })
    return results

def get_module_details_by_id(module_id, student_id=None):
    sql = text("""
        SELECT 
            c.*, 
            u.first_name AS instructor_first, 
            u.last_name AS instructor_last,
            (SELECT GROUP_CONCAT(pr.requires_module_id SEPARATOR ', ') 
             FROM prerequisites pr 
             WHERE pr.module_id = c.module_id) AS prereqs_list
        FROM modules c
        LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
        LEFT JOIN users u ON i.instructor_id = u.user_id
        WHERE c.module_id = :cid
    """)
    module = db.session.execute(sql, {"cid": module_id}).first()
    
    if not module: return None

    enrollment_status = None
    if student_id:
        enroll_sql = text("SELECT status FROM enrollments WHERE student_id = :sid AND module_id = :cid")
        enroll_record = db.session.execute(enroll_sql, {"sid": student_id, "cid": module_id}).first()
        if enroll_record: enrollment_status = enroll_record.status

    instructor_name = f"{module.instructor_first} {module.instructor_last}" if module.instructor_first else "TBA"
    curr = module.current_enrollment or 0
    
    return {
        "module_id": module.module_id, 
        "module_code": module.module_code if hasattr(module, 'module_code') else None,
        "module_name": module.module_name,
        "credits": module.credits,
        "description": module.description,
        "academic_term": module.academic_term,
        "max_capacity": module.max_capacity,
        "current_enrollment": curr,
        "slots_left": module.max_capacity - curr,
        "instructor_name": instructor_name,
        "prerequisites": module.prereqs_list if module.prereqs_list else "None",
        "student_status": enrollment_status
    }

def get_module_details_by_ids_list(module_ids):
    if not module_ids: return []
    # For simplicity, calling singular function in loop (SQL optimization possible here but kept simple)
    return [get_module_details_by_id(cid) for cid in module_ids if cid]

# =====================================================
#  SQL WRITE OPERATIONS (COURSES)
# =====================================================

def create_module(data):
    try:
        if 'module_id' not in data or not data['module_id']: raise ValueError("ID Required")
        
        sql = text("""
            INSERT INTO modules (module_id, module_code, module_name, description, credits, academic_term, max_capacity, instructor_id)
            VALUES (:id, :code, :name, :desc, :credits, :term, :cap, :inst_id)
        """)
        db.session.execute(sql, {
            "id": data['module_id'],
            "code": data['module_code'] if 'module_code' in data else data['module_id'],
            "name": data['module_name'],
            "desc": data.get('description', ''),
            "credits": data.get('credits', 6),
            "term": data.get('academic_term', 'Fall 2025'),
            "cap": data.get('max_capacity', 30),
            "inst_id": data.get('instructor_id')
        })
        db.session.commit()
        return f"Module {data['module_id']} created (SQL)."
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Module ID exists.")

def update_module(module_id, data):
    sql = text("""
        UPDATE modules SET module_name=:name, description=:desc, credits=:credits, 
        academic_term=:term, max_capacity=:cap WHERE module_id=:id
    """)
    db.session.execute(sql, {
        "id": module_id,
        "name": data.get('module_name'),
        "desc": data.get('description'),
        "credits": data.get('credits'),
        "term": data.get('academic_term'),
        "cap": data.get('max_capacity')
    })
    db.session.commit()
    return f"Module {module_id} updated (SQL)."

def delete_module(module_id):
    db.session.execute(text("DELETE FROM modules WHERE module_id = :id"), {"id": module_id})
    db.session.commit()
    return f"Module {module_id} deleted (SQL)."

# =====================================================
#  SQL USER MANAGEMENT
# =====================================================

def get_all_users_detailed():
    sql = text("""
        SELECT u.user_id, u.university_id, u.first_name, u.last_name, u.email, u.role, u.is_active,
               s.major, i.department_code
        FROM users u
        LEFT JOIN students s ON u.user_id = s.student_id
        LEFT JOIN instructors i ON u.user_id = i.instructor_id
        ORDER BY u.date_joined DESC
    """)
    users = db.session.execute(sql).all()
    return [{
        "user_id": u.user_id, "university_id": u.university_id, 
        "name": f"{u.first_name} {u.last_name}", "email": u.email, "role": u.role,
        "is_active": bool(u.is_active),
        "details": u.major if u.role == 'student' else (u.department_code if u.role == 'instructor' else 'Admin')
    } for u in users]

def create_user(data):
    try:
        sql_user = text("INSERT INTO users (university_id, email, password_hash, first_name, last_name, role, is_active) VALUES (:uid, :email, 'pass', :fname, :lname, :role, 1)")
        db.session.execute(sql_user, {
            "uid": data['university_id'], "email": data['email'], "fname": data['first_name'],
            "lname": data['last_name'], "role": data['role']
        })
        # Get ID
        uid_res = db.session.execute(text("SELECT user_id FROM users WHERE university_id=:uid"), {"uid": data['university_id']}).first()
        new_id = uid_res.user_id

        if data['role'] == 'student':
            db.session.execute(text("INSERT INTO students (student_id, major, enrollment_year) VALUES (:id, :major, :year)"), 
                               {"id": new_id, "major": data.get('major'), "year": data.get('enrollment_year', 2025)})
        elif data['role'] == 'instructor':
            db.session.execute(text("INSERT INTO instructors (instructor_id, department_code, title) VALUES (:id, :dept, :title)"), 
                               {"id": new_id, "dept": data.get('department_code'), "title": data.get('title')})
        
        db.session.commit()
        return "User created (SQL)."
    except Exception as e:
        db.session.rollback()
        raise e

def update_user(user_id, data):
    sql = text("UPDATE users SET first_name=:fname, last_name=:lname, email=:email WHERE user_id=:id")
    db.session.execute(sql, {"fname":data['first_name'], "lname":data['last_name'], "email":data['email'], "id":user_id})
    
    if data.get('role') == 'student':
        db.session.execute(text("UPDATE students SET major=:major, enrollment_year=:year WHERE student_id=:id"),
                           {"major":data.get('major'), "year":data.get('enrollment_year'), "id":user_id})
    elif data.get('role') == 'instructor':
        db.session.execute(text("UPDATE instructors SET department_code=:dept, title=:title WHERE instructor_id=:id"),
                           {"dept":data.get('department_code'), "title":data.get('title'), "id":user_id})
    
    db.session.commit()
    return "User updated (SQL)."

def delete_user(user_id):
    db.session.execute(text("DELETE FROM users WHERE user_id=:id"), {"id": user_id})
    db.session.commit()
    return "User deleted (SQL)."

def get_user_full_details(user_id):
    sql = text("""
        SELECT u.*, s.major, s.enrollment_year, i.department_code, i.title
        FROM users u
        LEFT JOIN students s ON u.user_id = s.student_id
        LEFT JOIN instructors i ON u.user_id = i.instructor_id
        WHERE u.user_id = :id
    """)
    row = db.session.execute(sql, {"id": user_id}).first()
    if row:
        return {
            "user_id": row.user_id, "first_name": row.first_name, "last_name": row.last_name, 
            "email": row.email, "role": row.role, "university_id": row.university_id,
            "major": row.major, "enrollment_year": row.enrollment_year,
            "department_code": row.department_code, "title": row.title
        }
    return None

def toggle_user_status(user_id):
    db.session.execute(text("UPDATE users SET is_active = NOT is_active WHERE user_id=:id"), {"id":user_id})
    db.session.commit()
    return "Status toggled (SQL)."

# =====================================================
#  SQL ENROLLMENT & MISC
# =====================================================

def enroll_student_in_module(student_id, module_id):
    try:
        # Check existing
        exist = db.session.execute(text("SELECT 1 FROM enrollments WHERE student_id=:sid AND module_id=:cid"), {"sid":student_id, "cid":module_id}).first()
        if exist: raise ValueError("Already enrolled")
        
        db.session.execute(text("INSERT INTO enrollments (student_id, module_id, status) VALUES (:sid, :cid, 'Enrolled')"), {"sid":student_id, "cid":module_id})
        db.session.execute(text("UPDATE modules SET current_enrollment = current_enrollment + 1 WHERE module_id=:cid"), {"cid": module_id})
        db.session.commit()
        return "Enrolled successfully (SQL)."
    except Exception as e:
        db.session.rollback()
        raise ValueError(str(e))

def drop_student_enrollment_module(student_id, module_id):
    db.session.execute(text("DELETE FROM enrollments WHERE student_id=:sid AND module_id=:cid"), {"sid":student_id, "cid":module_id})
    db.session.execute(text("UPDATE modules SET current_enrollment = current_enrollment - 1 WHERE module_id=:cid"), {"cid": module_id})
    db.session.commit()
    return "Dropped successfully (SQL)."

def get_student_enrollments(student_id):
    sql = text("""
        SELECT 
            e.module_id, 
            c.module_name, 
            c.credits, 
            c.academic_term,
            e.status, 
            e.final_grade,
            u.first_name, 
            u.last_name
        FROM enrollments e
        JOIN modules c ON e.module_id = c.module_id
        LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
        LEFT JOIN users u ON i.instructor_id = u.user_id
        WHERE e.student_id = :sid
    """)
    
    rows = db.session.execute(sql, {"sid": student_id}).all()
    
    return [{
        "module_id": r.module_id, 
        "module_name": r.module_name, 
        "credits": r.credits, 
        "academic_term": r.academic_term, 
        "status": r.status, 
        "final_grade": r.final_grade,
        # Combine names, default to "TBA" if null
        "instructor_name": f"{r.first_name} {r.last_name}" if r.first_name else "TBA"
    } for r in rows]

def get_student_data():
    sql = text("SELECT s.student_id, u.university_id, u.first_name, u.last_name, s.major FROM students s JOIN users u ON s.student_id = u.user_id")
    rows = db.session.execute(sql).all()
    return [{"id": r.student_id, "university_id": r.university_id, "name": f"{r.first_name} {r.last_name}", "major": r.major} for r in rows]

def get_instructor_data():
    sql = text("SELECT i.instructor_id, u.first_name, u.last_name, i.department_code, i.title FROM instructors i JOIN users u ON i.instructor_id = u.user_id")
    rows = db.session.execute(sql).all()
    return [{"id": r.instructor_id, "name": f"{r.first_name} {r.last_name}", "department_code": r.department_code, "title": r.title} for r in rows]

def get_user_data():
    rows = db.session.execute(text("SELECT user_id, email, first_name, last_name, role FROM users")).all()
    return [{"id": r.user_id, "email": r.email, "name": f"{r.first_name} {r.last_name}", "role": r.role} for r in rows]

def get_student_details_by_user_id(user_id):
    # Updated query to include 'major_id'
    sql = text("SELECT student_id, enrollment_year, major, major_id FROM students WHERE student_id = :uid")
    student = db.session.execute(sql, {"uid": user_id}).first()
    
    if student:
        return {
            "id": student.student_id, 
            "enrollment_year": student.enrollment_year, 
            "major": student.major,
            "major_id": student.major_id # <--- NEW: Return the short code (e.g. 'SE')
        }
    return None

def get_instructor_details_by_user_id(uid):
    row = db.session.execute(text("SELECT * FROM instructors WHERE instructor_id=:uid"), {"uid": uid}).first()
    return {"id": row.instructor_id, "department_code": row.department_code, "title": row.title} if row else None

def get_instructor_modules(iid):
    rows = db.session.execute(text("SELECT * FROM modules WHERE instructor_id=:iid"), {"iid": iid}).all()
    return [{"module_id": r.module_id, "module_name": r.module_name, "current_enrollment": r.current_enrollment, "max_capacity": r.max_capacity} for r in rows]

def get_students_in_module(cid):
    sql = text("SELECT s.student_id, u.first_name, u.last_name, s.major, u.university_id FROM students s JOIN enrollments e ON s.student_id=e.student_id JOIN users u ON s.student_id=u.user_id WHERE e.module_id=:cid")
    rows = db.session.execute(sql, {"cid": cid}).all()
    return [{"id": r.student_id, "name": f"{r.first_name} {r.last_name}", "major": r.major, "university_id": r.university_id} for r in rows]

def get_instructors_by_name(query: str) -> List[Dict[str, Any]]:
    """Search instructors by name (SQL version) with partial matching."""
    query_like = f"%{query}%"
    sql = text("""
        SELECT i.instructor_id, u.first_name, u.last_name, i.department_code, i.title
        FROM instructors i
        JOIN users u ON i.instructor_id = u.user_id
        WHERE u.first_name LIKE :q
           OR u.last_name LIKE :q
           OR CONCAT(u.first_name, ' ', u.last_name) LIKE :q
    """)
    rows = db.session.execute(sql, {"q": query_like}).all()
    return [
        {
            "id": r.instructor_id,
            "name": f"{r.first_name} {r.last_name}",
            "department_code": r.department_code,
            "title": r.title
        }
        for r in rows]
def get_instructors_by_name_and_dept(query: str) -> List[Dict[str, Any]]:
    """Search instructors by name (SQL version) with dept limit."""
    dept_constr, name_part = map(str.strip, query.split(':', 1))
    query_like = f"%{name_part}%"
    sql = text("""
        SELECT i.instructor_id, u.first_name, u.last_name, i.department_code, i.title
        FROM instructors i
        JOIN users u ON i.instructor_id = u.user_id
        WHERE (LOWER(u.first_name) LIKE LOWER(:q)
            OR LOWER(u.last_name) LIKE LOWER(:q)
            OR LOWER(CONCAT(u.first_name, ' ', u.last_name)) LIKE LOWER(:q))
          AND LOWER(i.department_code) = LOWER(:dept)
    """)

    rows = db.session.execute(sql, {"q": query_like, "dept": dept_constr}).all()

    return [
        {
            "id": r.instructor_id,
            "name": f"{r.first_name} {r.last_name}",
            "department_code": r.department_code,
            "title": r.title
        }
        for r in rows
    ]

# All functions are now module-prefixed following full rename
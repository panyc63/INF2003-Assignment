from .. import mongo
from datetime import datetime
from typing import Dict, Any, List

# =====================================================
#  MONGODB READ OPERATIONS
# =====================================================

def get_module_data():
    modules = list(mongo.db.modules.find())
    results = []
    for c in modules:
        # 1. Handle Capacity/Enrollment Math
        max_cap = c.get('max_capacity')
        curr_enroll = c.get('current_enrollment')
        
        slots_left = None
        if max_cap is not None and curr_enroll is not None:
            slots_left = max_cap - curr_enroll

        # 2. Handle Instructor Name (Manual Join)
        instructor_name = c.get('instructor_name')
        if not instructor_name and c.get('instructor_id'):
            inst = mongo.db.users.find_one({"user_id": c.get('instructor_id')})
            if inst:
                instructor_name = f"{inst.get('first_name')} {inst.get('last_name')}"
            else:
                instructor_name = "TBA"

        # 3. FIX: Robust Date Handling
        raw_date = c.get('created_at')
        if isinstance(raw_date, datetime):
            final_date = raw_date.isoformat()
        elif raw_date:
            final_date = str(raw_date)
        else:
            final_date = datetime.now().isoformat()

        results.append({
            "module_id": c.get('module_id'),
            "module_code": c.get('module_code') or c.get('module_id'), # Fallback
            "module_name": c.get('module_name'),
            "description": c.get('description'),
            "prerequisites": c.get('prerequisites'), 
            "credits": c.get('credits'),
            "academic_term": c.get('academic_term'),
            "max_capacity": max_cap,
            "current_enrollment": curr_enroll,
            "slots_left": slots_left,
            "instructor_name": instructor_name, 
            "created_at": final_date
        })
    return results

def get_module_details_by_id(module_id, student_id=None):
    module = mongo.db.modules.find_one({"module_id": module_id})
    if not module: return None
    
    enrollment_status = None
    if student_id:
        enroll = mongo.db.enrollments.find_one({"student_id": int(student_id), "module_id": module_id})
        if enroll: enrollment_status = enroll.get('status')

    curr = module.get('current_enrollment')
    cap = module.get('max_capacity')
    
    slots_left = None
    if cap is not None and curr is not None:
        slots_left = cap - curr

    # Handle Instructor Name
    instructor_name = module.get('instructor_name')
    if not instructor_name and module.get('instructor_id'):
        inst = mongo.db.users.find_one({"user_id": module.get('instructor_id')})
        if inst:
            instructor_name = f"{inst.get('first_name')} {inst.get('last_name')}"
        else:
            instructor_name = "TBA"

    return {
        "module_id": module.get('module_id'),
        "module_code": module.get('module_code'),
        "module_name": module.get('module_name'),
        "credits": module.get('credits'),
        "description": module.get('description'),
        "academic_term": module.get('academic_term'),
        "max_capacity": cap,
        "current_enrollment": curr,
        "slots_left": slots_left,
        "instructor_name": instructor_name,
        "prerequisites": module.get('prerequisites'),
        "student_status": enrollment_status
    }

def get_module_details_by_ids_list(module_ids: List[str]) -> List[Dict[str, Any]]:
    if not module_ids: return []
    modules = list(mongo.db.modules.find({"module_id": {"$in": module_ids}}))
    # Use helper to ensure consistent formatting
    return [get_module_details_by_id(c['module_id']) for c in modules]

# =====================================================
#  MONGODB WRITE OPERATIONS (moduleS)
# =====================================================

def create_module(data):
    if mongo.db.modules.find_one({"module_id": data['module_id']}):
        raise ValueError("Module ID exists (Mongo).")
    
    # Look up Instructor Name
    instructor_name = "TBA"
    inst_id = data.get('instructor_id')
    if inst_id:
        try:
            inst_id = int(inst_id)
        except: pass
        inst_user = mongo.db.users.find_one({"user_id": inst_id})
        if inst_user:
            instructor_name = f"{inst_user.get('first_name')} {inst_user.get('last_name')}"

    mongo.db.modules.insert_one({
        "module_id": data['module_id'],
        "module_code": data.get('module_code'), 
        "module_name": data['module_name'],
        "description": data.get('description'),
        "credits": data.get('credits'),
        "academic_term": data.get('academic_term'),
        "max_capacity": data.get('max_capacity'),
        "current_enrollment": 0,
        "created_at": datetime.now().isoformat(), 
        "instructor_id": inst_id,
        "instructor_name": instructor_name
    })
    return f"Module {data['module_id']} created (Mongo)."

def update_module(module_id, data):
    update_payload = {
        "module_name": data.get('module_name'),
        "description": data.get('description'),
        "credits": data.get('credits'),
        "academic_term": data.get('academic_term'),
        "max_capacity": data.get('max_capacity')
    }
    
    if 'instructor_id' in data:
        inst_id = int(data['instructor_id'])
        update_payload['instructor_id'] = inst_id
        inst_user = mongo.db.users.find_one({"user_id": inst_id})
        if inst_user:
             update_payload['instructor_name'] = f"{inst_user.get('first_name')} {inst_user.get('last_name')}"
        
    res = mongo.db.modules.update_one(
        {"module_id": module_id},
        {"$set": update_payload}
    )
    if res.matched_count == 0: raise ValueError("Module not found")
    return f"Module {module_id} updated (Mongo)."

def delete_module(module_id):
    res = mongo.db.modules.delete_one({"module_id": module_id})
    if res.deleted_count == 0: raise ValueError("Module not found")
    return f"Module {module_id} deleted (Mongo)."

# =====================================================
#  MONGODB USER MANAGEMENT
# =====================================================

def get_all_users_detailed():
    users = list(mongo.db.users.find())
    return [{
        "user_id": u.get('user_id'), 
        "university_id": u.get('university_id'), 
        "name": f"{u.get('first_name')} {u.get('last_name')}", 
        "email": u.get('email'), 
        "role": u.get('role'),
        "is_active": u.get('is_active'),
        "details": u.get('major') if u.get('role') == 'student' else u.get('dept')
    } for u in users]

def create_user(data):
    last_user = list(mongo.db.users.find().sort("user_id", -1).limit(1))
    new_id = 1 if not last_user else last_user[0]['user_id'] + 1
    
    user_doc = {
        "user_id": new_id,
        "university_id": data['university_id'],
        "email": data['email'],
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "role": data['role'],
        "is_active": True
    }
    
    if data.get('major'): user_doc['major'] = data['major']
    if data.get('enrollment_year'): user_doc['enrollment_year'] = data['enrollment_year']
    if data.get('department_code'): user_doc['dept'] = data['department_code']
    if data.get('title'): user_doc['title'] = data['title']

    mongo.db.users.insert_one(user_doc)
    return "User created (Mongo)."

def update_user(user_id, data):
    update_fields = {
        "first_name": data.get('first_name'),
        "last_name": data.get('last_name'),
        "email": data.get('email')
    }
    if data.get('role') == 'student':
        update_fields.update({"major": data.get('major'), "enrollment_year": data.get('enrollment_year')})
    elif data.get('role') == 'instructor':
        update_fields.update({"dept": data.get('department_code'), "title": data.get('title')})
        
    mongo.db.users.update_one({"user_id": user_id}, {"$set": update_fields})
    return "User updated (Mongo)."

def delete_user(user_id):
    res = mongo.db.users.delete_one({"user_id": user_id})
    if res.deleted_count == 0: raise ValueError("User not found")
    return "User deleted (Mongo)."

def get_user_full_details(user_id):
    u = mongo.db.users.find_one({"user_id": user_id})
    if u:
        return {
            "user_id": u.get('user_id'), 
            "university_id": u.get('university_id'),
            "first_name": u.get('first_name'), 
            "last_name": u.get('last_name'),
            "email": u.get('email'), 
            "role": u.get('role'),
            "major": u.get('major'), 
            "enrollment_year": u.get('enrollment_year'),
            "department_code": u.get('dept'), 
            "title": u.get('title')
        }
    return None

def toggle_user_status(user_id):
    user = mongo.db.users.find_one({"user_id": user_id})
    if user:
        new_status = not user.get('is_active')
        mongo.db.users.update_one({"user_id": user_id}, {"$set": {"is_active": new_status}})
        return "Status toggled (Mongo)."
    return "User not found."

# =====================================================
#  MONGODB ENROLLMENT & MISC
# =====================================================

def enroll_student_in_module(student_id, module_id):
    if mongo.db.enrollments.find_one({"student_id": student_id, "module_id": module_id}):
        raise ValueError("Already enrolled")
        
    mongo.db.enrollments.insert_one({
        "student_id": student_id,
        "module_id": module_id,
        "status": "Enrolled",
        "semester": "Trimester 1", # Should match your academic_term logic
        "date": datetime.now().isoformat()
    })
    mongo.db.modules.update_one({"module_id": module_id}, {"$inc": {"current_enrollment": 1}})
    return "Enrolled successfully (Mongo)."

def drop_student_enrollment_module(student_id, module_id):
    res = mongo.db.enrollments.delete_one({"student_id": student_id, "module_id": module_id})
    if res.deleted_count > 0:
        mongo.db.modules.update_one({"module_id": module_id}, {"$inc": {"current_enrollment": -1}})
        return "Dropped successfully (Mongo)."
    raise ValueError("Enrollment not found")

def get_student_enrollments(student_id):
    enrolls = list(mongo.db.enrollments.find({"student_id": student_id}))
    results = []
    for e in enrolls:
        c = mongo.db.modules.find_one({"module_id": e['module_id']})
        if c:
            # Fetch instructor name if not present in module doc
            instructor_name = c.get('instructor_name') or "TBA"
            
            results.append({
                "module_id": c.get('module_id'), 
                "module_name": c.get('module_name'), 
                "credits": c.get('credits'),
                "academic_term": c.get('academic_term'), 
                "status": e.get('status'), 
                "final_grade": e.get('final_grade'),
                "semester": c.get('academic_term'), # Map for frontend
                "instructor_name": instructor_name
            })
    return results

def get_student_data():
    students = list(mongo.db.users.find({"role": "student"}))
    return [{
        "id": s.get('user_id'), 
        "university_id": s.get('university_id'), 
        "name": f"{s.get('first_name')} {s.get('last_name')}", 
        "major": s.get('major')
    } for s in students]

def get_instructor_data():
    instructors = list(mongo.db.users.find({"role": "instructor"}))
    return [{
        "id": i.get('user_id'), 
        "name": f"{i.get('first_name')} {i.get('last_name')}", 
        "department_code": i.get('dept'), 
        "title": i.get('title')
    } for i in instructors]

def get_user_data():
    users = list(mongo.db.users.find())
    return [{
        "id": u.get('user_id'), 
        "email": u.get('email'), 
        "name": f"{u.get('first_name')} {u.get('last_name')}", 
        "role": u.get('role')
    } for u in users]

def get_student_details_by_user_id(uid):
    u = mongo.db.users.find_one({"user_id": uid, "role": "student"})
    if u:
        return {
            "id": u.get('user_id'), 
            "enrollment_year": u.get('enrollment_year'), 
            "major": u.get('major'),
            "major_id": u.get('major_id') # <--- NEW: Added for Search
        }
    return None

def get_instructor_details_by_user_id(uid):
    u = mongo.db.users.find_one({"user_id": uid, "role": "instructor"})
    if u:
        return {
            "id": u.get('user_id'), 
            "department_code": u.get('dept'), 
            "title": u.get('title')
        }
    return None

def get_instructor_modules(iid):
    modules = list(mongo.db.modules.find({"instructor_id": iid}))
    return [{
        "module_id": c.get('module_id'), 
        "module_name": c.get('module_name'), 
        "current_enrollment": c.get('current_enrollment'), 
        "max_capacity": c.get('max_capacity')
    } for c in modules]

def get_students_in_module(cid):
    enrolls = list(mongo.db.enrollments.find({"module_id": cid, "status": "Enrolled"}))
    if not enrolls: return []
    
    s_ids = [e['student_id'] for e in enrolls]
    students = list(mongo.db.users.find({"user_id": {"$in": s_ids}}))
    return [{
        "id": s.get('user_id'), 
        "name": f"{s.get('first_name')} {s.get('last_name')}", 
        "major": s.get('major'), 
        "university_id": s.get('university_id')
    } for s in students]
    
def get_instructors_by_name(query: str):
    """Return a list of instructors matching the query (partial, case-insensitive)."""
    if not query:
        return []

    # Build a case-insensitive regex for partial matching
    regex = {"$regex": query, "$options": "i"}

    instructors = list(mongo.db.users.find({
        "role": "instructor",
        "$or": [
            {"first_name": regex},
            {"last_name": regex},
            {"$expr": {"$regexMatch": {
                "input": {"$concat": ["$first_name", " ", "$last_name"]},
                "regex": query,
                "options": "i"
            }}}
        ]
    }))

    return [
        {
            "id": i.get("user_id"),
            "name": f"{i.get('first_name')} {i.get('last_name')}",
            "department_code": i.get("dept"),
            "title": i.get("title")
        } 
        for i in instructors
    ]

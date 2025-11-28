from .. import mongo
from datetime import datetime
from typing import Dict, Any, List
import re
_embedding_model = None

def get_model():
    global _embedding_model
    if _embedding_model is None:
        print("⏳ Loading AI Model (First Run Only)...")
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model
# =====================================================
#  MONGODB READ OPERATIONS
# =====================================================
def search_modules_by_query(original_query, term=None, level=None, instructor=None, student_major=None):
    """Semantic Search for modules with Exact Match fallback."""
    if not original_query:
        return []

    # This checks the query for module codes such as INF2002, 2002, inf2002, etc.
    clean_query = original_query.replace(" ", "")
    module_code_pattern = re.compile(r'^(?:[a-zA-Z]{1,4})?\d{3,4}[a-zA-Z]?$')
    print(module_code_pattern.match(clean_query))
    
    # if the query is a module code, search for exact matches without semantic search
    if module_code_pattern.match(clean_query):
        # Look in 'modules' collection
        exact_matches = list(mongo.db.modules.find(
            # Your current query
            {"module_id": {"$regex": f".*{clean_query}$", "$options": "i"}},
            {"_id": 0, "module_id": 1}
        ))
        
        if exact_matches:
            module_ids = [res['module_id'] for res in exact_matches]
            hydrated_results = get_module_details_by_ids_list(module_ids)
            
            for res in hydrated_results:
                res['score'] = 1.0
                # Ensure module_code exists (it's same as module_id)
                res['module_code'] = res['module_id']
            
            return hydrated_results

    # if the query is not a module code, perform semantic search with sentence transformers
    query_vector = get_model().encode(original_query).tolist()
    
    filter_list = []
    
    # filter by term
    if term:
        filter_list.append({"academic_term": {"$eq": term}})
    
    # filter by level
    if level:
        try:
            filter_list.append({"module_level": {"$eq": int(level)}})
        except ValueError: pass 
    
    # filter by instructor
    if instructor:
        filter_list.append({"instructor_name": {"$eq": instructor}})

    # filter by major
    if student_major:
        filter_list.append({"target_majors": {"$eq": student_major}})

    vector_search_stage = {
        "index": "vector_index_search",
        "path": "embedding",
        "queryVector": query_vector,
        "numCandidates": 100,
        "limit": 10
    }

    # if there are filters, add them to the vector search stage
    if filter_list:
        vector_filter = filter_list[0] if len(filter_list) == 1 else {"$and": filter_list}
        vector_search_stage["filter"] = vector_filter
    
    # perform vector search
    pipeline = [
        {"$vectorSearch": vector_search_stage},
        {"$project": {"_id": 0, "module_id": 1, "score": { "$meta": "vectorSearchScore" }}}
    ]
    
    #  our aggregation pipeline
    try:
        mongo_results = list(mongo.db.modules.aggregate(pipeline))
    except Exception as e:
        print(f"Mongo Error: {e}")
        raise e

    if not mongo_results:
        return []

    module_ids = [res['module_id'] for res in mongo_results]
    hydrated_results = get_module_details_by_ids_list(module_ids)
    
    score_map = {res['module_id']: res['score'] for res in mongo_results}
    
    for res in hydrated_results:
        res['score'] = score_map.get(res['module_id'], 0)
        # Ensure module_code exists
        res['module_code'] = res['module_id']

    # sort results by score their embedding score as mongo, so highest matched search on top.
    hydrated_results.sort(key=lambda x: x.get('score', 0), reverse=True)
    return hydrated_results

# get modules data with instructor info (for homepage/ general modules query )
def get_module_data():
    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "instructor_id",
                "foreignField": "user_id",
                "as": "instructor_info"
            }
        },
        {
            "$unwind": {
                "path": "$instructor_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "module_id": 1,
                "module_code": 1,
                "module_name": 1,
                "description": 1,
                "prerequisites": 1,
                "credits": 1,
                "academic_term": 1,
                "max_capacity": 1,
                "current_enrollment": 1,
                "created_at": 1,
                # Concat name if exists, else TBA,
                "instructor_name": {
                    "$cond": {
                        "if": {"$ifNull": ["$instructor_name", False]},
                        "then": "$instructor_name",
                        "else": "TBA"
                    }
                }
            }
        }
    ]
    
    modules = list(mongo.db.modules.aggregate(pipeline))
    
    # python-side post-processing for logic hard to do in Aggregation
    results = []
    for c in modules:
        max_cap = c.get('max_capacity')
        curr_enroll = c.get('current_enrollment')
        slots_left = (max_cap - curr_enroll) if (max_cap is not None and curr_enroll is not None) else None
        
        # Handle date conversion
        raw_date = c.get('created_at')
        if isinstance(raw_date, datetime):
            final_date = raw_date.isoformat()
        else:
            final_date = str(raw_date) if raw_date else datetime.now().isoformat()

        results.append({
            **c, # Unpack fields from projection
            "module_code": c.get('module_code') or c.get('module_id'),
            "slots_left": slots_left,
            "created_at": final_date
        })
    return results

# get module details by id
def get_module_details_by_id(module_id, student_id=None):

    module = mongo.db.modules.find_one({"module_id": module_id})
    if not module: return None
    
    enrollment_status = None
    if student_id:
        enroll = mongo.db.enrollments.find_one({"student_id": int(student_id), "module_id": module_id})
        if enroll: enrollment_status = enroll.get('status')

    curr = module.get('current_enrollment')
    cap = module.get('max_capacity')
    slots_left = (cap - curr) if (cap is not None and curr is not None) else None

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

# get module details by list of ids
def get_module_details_by_ids_list(module_ids: List[str]) -> List[Dict[str, Any]]:
    # optimizable, but using loop to reuse get_module_details logic
    if not module_ids: return []
    modules = list(mongo.db.modules.find({"module_id": {"$in": module_ids}}))
    return [get_module_details_by_id(c['module_id']) for c in modules]


# =====================================================
#  MONGODB WRITE OPERATIONS & USERS (Kept standard)
# =====================================================

# create module
def create_module(data):
    if mongo.db.modules.find_one({"module_id": data['module_id']}):
        raise ValueError("Module ID exists (Mongo).")

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

# update individual module
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

# get all users detailed
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

# create user
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

# update user
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

# delete user
def delete_user(user_id):
    res = mongo.db.users.delete_one({"user_id": user_id})
    if res.deleted_count == 0: raise ValueError("User not found")
    return "User deleted (Mongo)."

# get user full details
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

# activate/deactivate user
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

# enroll student in module
def enroll_student_in_module(student_id, module_id):
    if mongo.db.enrollments.find_one({"student_id": student_id, "module_id": module_id}):
        raise ValueError("Already enrolled")
        
    mongo.db.enrollments.insert_one({
        "student_id": student_id,
        "module_id": module_id,
        "status": "Enrolled",
        "semester": "Trimester 1", 
        "date": datetime.now().isoformat()
    })
    mongo.db.modules.update_one({"module_id": module_id}, {"$inc": {"current_enrollment": 1}})
    return "Enrolled successfully (Mongo)."

# drop student enrollment in module
def drop_student_enrollment_module(student_id, module_id):
    res = mongo.db.enrollments.delete_one({"student_id": student_id, "module_id": module_id})
    if res.deleted_count > 0:
        mongo.db.modules.update_one({"module_id": module_id}, {"$inc": {"current_enrollment": -1}})
        return "Dropped successfully (Mongo)."
    raise ValueError("Enrollment not found")

# get student enrollments
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

# get all students 
def get_student_data():
    students = list(mongo.db.users.find({"role": "student"}))
    return [{
        "id": s.get('user_id'), 
        "university_id": s.get('university_id'), 
        "name": f"{s.get('first_name')} {s.get('last_name')}", 
        "major": s.get('major')
    } for s in students]

# get all instructors
def get_instructor_data():
    pipeline = [
        {"$match": {"role": "instructor"}},
        {"$lookup": {
            "from": "instructors",
            "localField": "user_id",
            "foreignField": "instructor_id",
            "as": "instructor_details"
        }},
        {"$unwind": {
            "path": "$instructor_details",
            "preserveNullAndEmptyArrays": True
        }},
        {"$project": {
            "user_id": 1,
            "first_name": 1,
            "last_name": 1,
            "department_code": "$instructor_details.department_code",
            "title": "$instructor_details.title"
        }}
    ]
    instructors = list(mongo.db.users.aggregate(pipeline))
    return [{
        "id": i.get('user_id'), 
        "name": f"{i.get('first_name')} {i.get('last_name')}", 
        "department_code": i.get('department_code'), 
        "title": i.get('title')
    } for i in instructors]

# get all users
def get_user_data():
    users = list(mongo.db.users.find())
    return [{
        "id": u.get('user_id'), 
        "email": u.get('email'), 
        "name": f"{u.get('first_name')} {u.get('last_name')}", 
        "role": u.get('role')
    } for u in users]

# get student details by user id
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

# get instructor details by user id
def get_instructor_details_by_user_id(uid):
    u = mongo.db.users.find_one({"user_id": uid, "role": "instructor"})
    if u:
        return {
            "id": u.get('user_id'), 
            "department_code": u.get('dept'), 
            "title": u.get('title')
        }
    return None

# get modules taught by instructor
def get_instructor_modules(iid):
    modules = list(mongo.db.modules.find({"instructor_id": iid}))
    return [{
        "module_id": c.get('module_id'), 
        "module_name": c.get('module_name'), 
        "current_enrollment": c.get('current_enrollment'), 
        "max_capacity": c.get('max_capacity')
    } for c in modules]

# get students in module
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
    
# get instructors by name
def get_instructors_by_name(query: str):
    if not query:
        return []

    pipeline = [
        {
            "$match": {
                "role": "instructor",
                "$or": [
                    {"first_name": {"$regex": query, "$options": "i"}},
                    {"last_name": {"$regex": query, "$options": "i"}},
                    {"$expr": {"$regexMatch": {
                        "input": {"$concat": ["$first_name", " ", "$last_name"]},
                        "regex": query,
                        "options": "i"
                    }}}
                ]
            }
        },
        {
            "$lookup": {
                "from": "instructors",
                "localField": "user_id",
                "foreignField": "instructor_id",
                "as": "instructor_details"
            }
        },
        {
            "$unwind": "$instructor_details"
        },
        {
            "$project": {
                "user_id": 1,
                "first_name": 1,
                "last_name": 1,
                "department_code": "$instructor_details.department_code",
                "title": "$instructor_details.title"
            }
        }
    ]

    instructors = list(mongo.db.users.aggregate(pipeline))

    return [
        {
            "id": i.get("user_id"),
            "name": f"{i.get('first_name')} {i.get('last_name')}",
            "department_code": i.get("department_code"),
            "title": i.get("title")
        } 
        for i in instructors
    ]

# get instructors by name and department
def get_instructors_by_name_and_dept(query: str):
    if not query:
        return []

    dept_code, name_part = map(str.strip, query.split(':', 1))
    
    pipeline = [
        {
            "$match": {
                "role": "instructor",
                "$or": [
                    {"first_name": {"$regex": name_part, "$options": "i"}},
                    {"last_name": {"$regex": name_part, "$options": "i"}},
                    {"$expr": {"$regexMatch": {
                        "input": {"$concat": ["$first_name", " ", "$last_name"]},
                        "regex": name_part,
                        "options": "i"
                    }}}
                ]
            }
        },
        {
            "$lookup": {
                "from": "instructors",
                "localField": "user_id",
                "foreignField": "instructor_id",
                "as": "instructor_details"
            }
        },
        {
            "$unwind": "$instructor_details"
        },
        {
            "$match": {
                "instructor_details.department_code": {"$regex": f"^{dept_code}$", "$options": "i"}
            }
        },
        {
            "$project": {
                "user_id": 1,
                "first_name": 1,
                "last_name": 1,
                "department_code": "$instructor_details.department_code",
                "title": "$instructor_details.title"
            }
        }
    ]

    instructors = list(mongo.db.users.aggregate(pipeline))

    return [
        {
            "id": i.get("user_id"),
            "name": f"{i.get('first_name')} {i.get('last_name')}",
            "department_code": i.get("department_code"),
            "title": i.get("title")
        } 
        for i in instructors
    ]


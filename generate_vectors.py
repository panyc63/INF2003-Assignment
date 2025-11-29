# THIS PYTHON FILE GETS DATA FROM SQL POPULATES MONGODB, 
# THIS FILE IS NOT MEANT TO BE RAN EVERYTIME
# AND ALSO GENERATES EMBEDDINGS FOR MODULES AND USERS
import numpy as np
from sentence_transformers import SentenceTransformer
from website import create_app
from website.models import Module, User, Instructor, Student
from website import db as sql_db
from website import mongo
from sqlalchemy.orm import aliased
import re

def generate_and_store_embeddings():
    """
    1. Fetches MODULES, embeds descriptions, stores in Mongo 'modules'.
    2. Fetches USERS (linked with Student/Instructor details), embeds info, stores in Mongo 'users'.
    """
    print("--- STEP 1: Starting Script ---")

    # 1. Load the pre-trained NLP model
    print("--- STEP 2: Loading NLP Model (This takes time on first run)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("--- STEP 2: DONE. Model Loaded. ---")

    # 2. Connect to databases
    app = create_app()
    
    # We use the app context to access the database configured in create_app()
    with app.app_context():
        print("--- STEP 3: Connecting to SQL Database... ---")

        # ==========================================
        # PART A: PROCESS MODULES
        # ==========================================
        print("\n--- [PART A] Processing MODULES ---")
        
        InstructorUser = aliased(User)
        
        # UPDATED QUERY: We use .label() to avoid ambiguity and ensure we get the right columns
        sql_modules = sql_db.session.query(
            Module.module_id,
            Module.module_name,
            Module.description,
            Module.credits,
            Module.academic_term,
            Module.max_capacity,
            Module.current_enrollment,
            Module.target_majors,
            InstructorUser.first_name.label('instr_first'), 
            InstructorUser.last_name.label('instr_last')    
        ).outerjoin(Module.instructor)\
         .outerjoin(Instructor.user.of_type(InstructorUser))\
         .all()

        if sql_modules:
            print(f"Found {len(sql_modules)} modules in SQL.")
            
            modules_collection = mongo.db.modules
            modules_collection.delete_many({}) 

            module_docs = []
            for module in sql_modules:
                if not module.description:
                    continue

                # --- LOGIC FIX ---
                # We check truthiness (if module.instr_first) which catches both None and Empty Strings
                if module.instr_first and module.instr_last:
                    instructor_name = f"{module.instr_first} {module.instr_last}"
                else:
                    instructor_name = "TBA"
                
                # UPDATED EMBEDDING TEXT
                text_to_embed = (
                    f"{module.module_id} {module.module_name}: {module.description}. "
                    f"Taught by {instructor_name}. "
                    f"Credits: {module.credits}. "
                    f"Term: {module.academic_term}."
                )
                
                embedding = model.encode(text_to_embed).tolist()

                
                # Logic for level extraction
                module_level = 1000
                match = re.search(r'\d', module.module_id)
                if match:
                    module_level = int(match.group()) * 1000

                # Logic for slots
                cap = module.max_capacity if module.max_capacity is not None else 0
                curr = module.current_enrollment if module.current_enrollment is not None else 0
                slots_left = cap - curr

                # Clean up target majors
                majors_list = [m.strip() for m in module.target_majors.split(',')] if module.target_majors else ["All"]

                mongo_doc = {
                    "module_id": module.module_id,
                    "module_name": module.module_name,
                    "description": module.description,
                    "embedding": embedding,
                    "credits": module.credits,
                    "max_capacity": module.max_capacity,
                    "current_enrollment": module.current_enrollment,
                    "slots_left": slots_left,
                    "academic_term": module.academic_term,
                    "module_level": module_level,
                    "instructor_name": instructor_name,
                    "target_majors": majors_list,
                    "type": "module" 
                }
                module_docs.append(mongo_doc)

            if module_docs:
                modules_collection.insert_many(module_docs)
                print(f"Inserted {len(module_docs)} modules into MongoDB.")
        else:
            print("No modules found in SQL.")

        # ==========================================
        # PART B: PROCESS USERS
        # ==========================================
        print("\n--- [PART B] Processing USERS ---")

        # Fetch all users using the session directly to avoid context errors
        sql_users = sql_db.session.query(User).all()
        
        if sql_users:
            print(f"Found {len(sql_users)} users in SQL.")

            # Connect to Mongo Users Collection
            users_collection = mongo.db.users
            users_collection.delete_many({}) 
            mongo.db.instructors.delete_many({}) 

            user_docs = []
            for user in sql_users:
                # 1. Base Variables
                role_descriptor = user.role.capitalize()
                details = ""
                major_or_dept = ""

                # 2. Enrich based on Role (Querying Child Tables)
                if user.role == 'student':
                    # Use session.query instead of Model.query
                    student_info = sql_db.session.query(Student).get(user.user_id)
                    if student_info:
                        major_or_dept = student_info.major
                        details = f"Major: {student_info.major}. Year: {student_info.enrollment_year}. Standing: {student_info.current_standing}."
                        role_descriptor = "Student"
                
                elif user.role == 'instructor':
                    instructor_info = sql_db.session.query(Instructor).get(user.user_id)
                    if instructor_info:
                        major_or_dept = instructor_info.department_code

                        details = (
                            f"Title: {instructor_info.title}. "
                            f"Department: {instructor_info.department_code}. "
                            f"Office: {instructor_info.office_location}. "
                            f"Hours: {instructor_info.office_hours}."
                        )
                        role_descriptor = instructor_info.title 

              
                        mongo.db.instructors.insert_one({
                            "instructor_id": user.user_id,
                            "department_code": instructor_info.department_code,
                            "title": instructor_info.title,
                            "office_location": instructor_info.office_location,
                            "office_hours": instructor_info.office_hours
                        })

                # 3. Construct Text to Embed
                # We use the schema data to create a "Bio-like" string for the AI
                text_to_embed = f"{role_descriptor} {user.first_name} {user.last_name}. {details}"
                
                # 4. Generate Vector
                embedding = model.encode(text_to_embed).tolist()

                # 5. Create Mongo Document
                user_doc = {
                    "user_id": user.user_id, 
                    "university_id": user.university_id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": user.role,
                    "info": details, 
                    "context_key": major_or_dept, 
                    "embedding": embedding,
                    "type": "user"
                }
                user_docs.append(user_doc)

            # 6. Insert into Mongo
            if user_docs:
                users_collection.insert_many(user_docs)
                print(f"Inserted {len(user_docs)} users into MongoDB.")
            else:
                print("No eligible users to insert.")
        else:
            print("No users found in SQL.")

    print("\n--- Success! Database Population Complete. ---")

if __name__ == '__main__':
    generate_and_store_embeddings()
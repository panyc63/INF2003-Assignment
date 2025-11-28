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
        
        # Alias User to fetch Instructor names efficiently
        InstructorUser = aliased(User)
        
        sql_modules = sql_db.session.query(
            Module.module_id,
            Module.module_name,
            Module.description,
            Module.academic_term,
            Module.target_majors,
            InstructorUser.first_name,
            InstructorUser.last_name
        ).outerjoin(Module.instructor)\
         .outerjoin(Instructor.user.of_type(InstructorUser))\
         .all()

        if sql_modules:
            print(f"Found {len(sql_modules)} modules in SQL.")
            
            # Connect to Mongo Modules Collection
            modules_collection = mongo.db.modules
            modules_collection.delete_many({}) # Clear old data

            module_docs = []
            for module in sql_modules:
                if not module.description:
                    continue

                # Enrich Data for Embedding
                instructor_name = f"{module.first_name} {module.last_name}" if module.first_name else "TBA"
                
                # The text the AI will "read" to find this module
                text_to_embed = f"{module.module_id} {module.module_name}: {module.description}. Taught by {instructor_name}."
                
                embedding = model.encode(text_to_embed).tolist()

                # Extract Level (e.g., INF1002 -> 1000)
                module_level = 1000
                match = re.search(r'\d', module.module_id)
                if match:
                    module_level = int(match.group()) * 1000

                # Clean up target majors
                majors_list = []
                if module.target_majors:
                    majors_list = [m.strip() for m in module.target_majors.split(',') if m.strip()]
                else:
                    majors_list = ["All"]

                mongo_doc = {
                    "module_id": module.module_id,
                    "module_name": module.module_name,
                    "description": module.description,
                    "embedding": embedding,
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
            users_collection.delete_many({}) # Clear old data

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
                    # Use session.query instead of Model.query
                    instructor_info = sql_db.session.query(Instructor).get(user.user_id)
                    if instructor_info:
                        major_or_dept = instructor_info.department_code
                        details = f"Title: {instructor_info.title}. Department: {instructor_info.department_code}. Office: {instructor_info.office_location}."
                        role_descriptor = instructor_info.title # e.g., "Professor"

                # 3. Construct Text to Embed
                # We use the schema data to create a "Bio-like" string for the AI
                text_to_embed = f"{role_descriptor} {user.first_name} {user.last_name}. {details}"
                
                # 4. Generate Vector
                embedding = model.encode(text_to_embed).tolist()

                # 5. Create Mongo Document
                user_doc = {
                    "user_id": user.user_id, # SQL Primary Key
                    "university_id": user.university_id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": user.role,
                    "info": details, # Store the text details for display
                    "context_key": major_or_dept, # Store Major or Dept for filtering
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
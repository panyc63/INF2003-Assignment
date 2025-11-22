# generate_vectors.py
import numpy as np
from sentence_transformers import SentenceTransformer
from website import create_app
from website.models import Module, User, Instructor  
from website import db as sql_db   
from website import mongo
from sqlalchemy.orm import aliased 
import re # Needed for the regex match

def generate_and_store_embeddings():
    """
    Fetches modules WITH INSTRUCTOR NAMES from MySQL, generates embeddings,
    and stores them in MongoDB.
    """
    print("--- STEP 1: Starting Script ---") 

    # 1. Load the pre-trained NLP model
    print("--- STEP 2: Loading NLP Model (This takes time on first run)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("--- STEP 2: DONE. Model Loaded. ---")

    # 2. Connect to databases
    app = create_app()
    with app.app_context():
        print("--- STEP 3: Connecting to SQL Database... ---")

        # --- 1. MODIFIED SQL QUERY ---
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
        # -----------------------------

        if not sql_modules:
            print("Error: No modules found in SQL database.")
            return

        print(f"--- STEP 3: DONE. Found {len(sql_modules)} modules in SQL. ---")
        print("--- STEP 4: Connecting to MongoDB... (If it hangs here, check IP Whitelist) ---")

        mongo_collection = mongo.db.modules  # <-- Collection renamed to 'modules'
        mongo_collection.delete_many({}) 

        print("--- STEP 4: DONE. Connected to Mongo. Generating vectors... ---")

        mongo_docs = []
        for module in sql_modules:
            if not module.description:
                print(f"Skipping {module.module_name} (no description).")
                continue

            # --- 2. ENRICH THE DATA ---
            instructor_name = f"{module.first_name} {module.last_name}" if module.first_name else "TBA"
            
            text_to_embed = f"{module.module_name}: {module.description}. Taught by {instructor_name}."
            
            embedding = model.encode(text_to_embed).tolist()

            # Extract Level (e.g., INF1002 -> 1000)
            module_level = 1000 # Default
            match = re.search(r'\d', module.module_id)
            if match:
                first_digit = int(match.group()) 
                module_level = first_digit * 1000

            # Convert "SE,CS" string to ["SE", "CS"] List
            majors_list = []
            if module.target_majors:
                # Split string by comma, strip spaces
                majors_list = [m.strip() for m in module.target_majors.split(',') if m.strip()]
            else:
                majors_list = ["All"]

            # --- 3. CREATE MONGO DOCUMENT ---
            mongo_doc = {
                "module_id": module.module_id,
                "module_name": module.module_name,
                "description": module.description,
                "embedding": embedding,
                "academic_term": module.academic_term,
                "module_level": module_level,
                "instructor_name": instructor_name,
                "target_majors": majors_list 
            }
            mongo_docs.append(mongo_doc)

        if mongo_docs:
            print(f"Inserting {len(mongo_docs)} documents into MongoDB...")
            mongo_collection.insert_many(mongo_docs)
            print("\n--- Success! ---")
            print("Your MongoDB 'modules' collection is now populated.")
        else:
            print("No modules were inserted into MongoDB.")

if __name__ == '__main__':
    generate_and_store_embeddings()
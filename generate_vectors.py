# generate_vectors.py
import numpy as np
from sentence_transformers import SentenceTransformer
from website import create_app
from website.models import Course, User, Instructor  # <-- Import User and Instructor
from website import db as sql_db   
from website import mongo
from sqlalchemy.orm import aliased # <-- Import aliased

def generate_and_store_embeddings():
    """
    Fetches courses WITH INSTRUCTOR NAMES from MySQL, generates embeddings,
    and stores them in MongoDB.
    """

    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Loaded NLP model.")

    app = create_app()
    with app.app_context():
        print("Connecting to databases...")

        # --- 1. MODIFIED SQL QUERY ---
        # We create an "alias" for the User table to join it correctly
        InstructorUser = aliased(User)
        
        # This query now JOINS Course -> Instructor -> User
        sql_courses = sql_db.session.query(
            Course.course_id,
            Course.course_code,
            Course.course_name,
            Course.description,
            Course.academic_term,
            InstructorUser.first_name, # <-- Get instructor's first name
            InstructorUser.last_name   # <-- Get instructor's last name
        ).outerjoin(Course.instructor)\
         .outerjoin(Instructor.user.of_type(InstructorUser))\
         .all()
        # -----------------------------

        if not sql_courses:
            print("No courses found in SQL database.")
            return

        print(f"Found {len(sql_courses)} courses in SQL. Generating embeddings...")

        mongo_collection = mongo.db.courses
        mongo_collection.delete_many({})

        mongo_courses = []
        for course in sql_courses:
            if not course.description:
                print(f"Skipping {course.course_name} (no description).")
                continue

            # --- 2. ENRICH THE DATA ---
            # Create the full instructor name
            instructor_name = f"{course.first_name} {course.last_name}" if course.first_name else "TBA"
            
            # THIS IS THE MOST IMPORTANT CHANGE:
            # We add "Taught by..." to the text that will be vectorized.
            text_to_embed = f"{course.course_name}: {course.description}. Taught by {instructor_name}."
            # --------------------------
            
            embedding = model.encode(text_to_embed).tolist()

            course_level = 1000
            if course.course_code and course.course_code[3].isdigit():
                course_level = int(course.course_code[3]) * 1000

            # --- 3. ENRICH THE MONGO DOCUMENT ---
            mongo_doc = {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "description": course.description,
                "embedding": embedding,
                "academic_term": course.academic_term,
                "course_level": course_level,
                "instructor_name": instructor_name # <-- Add name for filtering
            }
            mongo_courses.append(mongo_doc)
            # ----------------------------------

        if mongo_courses:
            print(f"Inserting {len(mongo_courses)} documents into MongoDB...")
            mongo_collection.insert_many(mongo_courses)
            print("\n--- Success! ---")
            print("Your MongoDB 'courses' collection is now enriched with instructor names.")
        else:
            print("No courses were inserted into MongoDB.")

if __name__ == '__main__':
    generate_and_store_embeddings()
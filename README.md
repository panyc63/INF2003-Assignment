Here is a complete `README.md` file for your project.

You can save this file as `README.md` in your project's root folder (`INF2003-Assignment/README.md`).

-----

# University Course Management System (INF2003)

This is a Flask web application for the INF2003 Database Systems project. It uses a hybrid database system to manage university courses and provide a powerful, natural-language semantic search for students.

## 🚀 Features

  * **Hybrid Database System:** Uses MySQL for all structured, relational data (users, courses, enrollments) and MongoDB Atlas for a non-relational vector search index.
  * **True Semantic Search:** Search for courses using natural language (e.g., "programming courses by alan turing").
  * **Smart Filtering:** Combines semantic search with structured filters for academic term, course level, and instructor.
  * **Student Dashboard:** A personalized dashboard for students to view their academic history (from SQL) and search the global course catalog (from NoSQL).
  * **Realistic Data:** The SQL database is populated using real module data from 7 different SIT curriculum PDFs.

## 🏗️ System Architecture

  * **Backend:** Flask
  * **Relational Database (SQL):** MySQL
  * **Non-Relational Database (NoSQL):** MongoDB Atlas (for Vector Search)
  * **Semantic Model:** `sentence-transformers`

## 🏁 Getting Started

Follow these steps to set up and run the project on your local machine.

### 1\. Prerequisites

Before you begin, you will need:

  * Python 3.10+
  * A local MySQL server (e.g., XAMPP, MySQL Community Server)
  * A free MongoDB Atlas account

### 2\. Installation & Setup

**A. Clone the Repository & Set Up Environment**

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd INF2003-Assignment

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. Install all required packages
pip install -r requirements.txt
```

**B. Configure the SQL Database (MySQL)**

1.  Open your MySQL tool (like MySQL Workbench).
2.  Create a new database. We recommend using `inf2003-db`.
    ```sql
    CREATE DATABASE inf2003-db;
    ```
3.  Open the `config.py` file in the project root.
4.  Update the `SQLALCHEMY_DATABASE_URI` with your MySQL username, password, and database name.
    ```python
    # in config.py
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:YOUR_PASSWORD@localhost/inf2003-db'
    ```

**C. Configure the NoSQL Database (MongoDB Atlas)**

1.  Create a new, free **M0 cluster** on MongoDB Atlas.

2.  Under **Network Access**, add an IP Address. Click `ALLOW ACCESS FROM ANYWHERE` (`0.0.0.0/0`).

3.  Under **Database Access**, create a new database user (e.g., `inf2003-admin` with a password).

4.  Go to **Database**, click **Connect** \> **Drivers**, and copy your **Connection String**.

5.  Open `config.py` again.

6.  Update the `MONGO_URI` with your connection string. **Remember to add your database name (e.g., `ucms_db`)** before the `?`.

    ```python
    # in config.py
    MONGO_URI = "mongodb+srv://inf2003-admin:YOUR_PASSWORD@...mongodb.net/ucms_db?appName=Cluster0"
    ```

### 3\. Populate Your Databases (Required One-Time Step)

This is the most important step. You must populate your databases in this order.

**A. Populate SQL**

1.  Open your MySQL tool (Workbench) and connect to your `inf2003-db`.
2.  Open and run the **"Final, Complete SQL Reset Script"** I provided in our chat. This script will:
      * Create all tables (`users`, `courses`, `enrollments`, etc.).
      * Populate them with all the PDF-accurate course data.
      * Create your "Alex Cross" student profile and academic history.

**B. Populate NoSQL (Sync)**

1.  Now that your SQL database has data, you must sync it to MongoDB.
2.  In your terminal (with your `venv` active), run:
    ```bash
    python generate_vectors.py
    ```
3.  This script will read from your local MySQL, generate vectors for each course, and upload them to your MongoDB Atlas cluster.

### 4\. Create the Atlas Search Index

Your MongoDB cluster now has the data, but it isn't indexed for search.

1.  In your MongoDB Atlas dashboard, go to your `courses` collection.

2.  Click the **Search** tab.

3.  Click **Create Search Index** and select the **JSON Editor**.

4.  Set the **Index Name** to `vector_search`.

5.  In the JSON editor, paste this exact configuration:

    ```json
    {
      "fields": [
        {
          "type": "vector",
          "path": "embedding",
          "numDimensions": 384,
          "similarity": "cosine"
        },
        {
          "type": "filter",
          "path": "academic_term"
        },
        {
          "type": "filter",
          "path": "course_level"
        },
        {
          "type": "filter",
          "path": "instructor_name"
        }
      ]
    }
    ```

6.  Click **Create Index**. Wait 1-2 minutes for the status to change from "Building" to **"Active"**.

### 5\. Run the Application

You are all set\!

1.  In your terminal (with `venv` active), run the main application:
    ```bash
    python run.py
    ```
2.  Open your web browser and go to `http://127.0.0.1:5000`

-----

## ⚠️ Important Note on `generate_vectors.py`

You only need to run `python generate_vectors.py` **one time** during this setup.

**Do not run it again** unless you have made major changes to the `courses` or `instructors` tables in your SQL database and need to re-sync your search index.
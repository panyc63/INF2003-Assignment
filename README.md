# UCMS - University Course Management System

UCMS-University Course Management System is a modern, full-stack web application designed to revolutionize how university students discover and enroll in modules. It features a **Hybrid Database Architecture** (SQL & NoSQL), **Semantic Search** powered by AI, and a responsive, role-based user interface.

![UCMS](website/static/img/github.png)
## 🚀 Key Features

### 🔍 Semantic Search
- **Natural Language Processing**: Search for "courses about web design" and get results for "Web Application Development" even if the keywords don't match exactly.
- **Smart Filtering**: Automatically detects academic terms (e.g., "Year 1 Trimester 2") from your search query.
- **Hybrid Search**: Combines vector similarity search with traditional keyword matching.

### 🔀 Hybrid Database Architecture with one-one mapping
- **Dual-Backend Support**: Switch between **MySQL** and **MongoDB** in real-time using the toggle in the navigation bar.
- **Service Facade Pattern**: Clean architecture abstracting database logic from the API layer.
- **Advanced Aggregation**: Utilizes MongoDB aggregation pipelines for high-performance data retrieval.

### 👥 Role-Based Dashboards
- **Students**: View enrolled modules, check GPA/credits, and discover personalized recommendations.
- **Instructors**: Manage taught modules and view student enrollments.
- **Admins**: Full CRUD capabilities for Users and Modules.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Flask, SQLAlchemy, PyMongo
- **Database**: 
  - **MySQL** (Relational Data)
  - **MongoDB Atlas** (Vector Search & Document Store)
- **AI/ML**: `sentence-transformers` (Hugging Face)
- **Frontend**: HTML5, TailwindCSS, Bootstrap 4, Vanilla JavaScript

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- MongoDB Atlas Cluster (for Vector Search)

### 1. Clone the Repository
```bash
git clone https://github.com/panyc63/INF2003-Assignment.git
cd INF2003-Assignment
```
### 2. Create virtual environment and activate it
```bash
python3 -m venv .venv
\.venv\Scripts\activate.bat
```
### 3. Install Dependencies (Will take a few minutes)
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
If you wish to use the original cloud service, you do not need to change anything.
If you wish to use your own database, create a `.env` file or update `config.py` with your database credentials:
```python
# config.py
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/inf2003_db'
MONGO_URI = 'mongodb+srv://<user>:<password>@cluster.mongodb.net/inf2003_db'
```

### 5. Initialize Databases
Do not need to run this if using cloud server
(Only if using local servers) Run the initialization script to populate MongoDB and generate embeddings for MongoDB:
```bash
python generate_vectors.py
```
Populate MySQL with the providede script.

### 6. Run the Application
```bash
python run.py
```
Visit `http://127.0.0.1:5000/` in your browser.

---

## 📂 Project Structure

```
INF2003-Assignment/
├── website/
│   ├── routes/             # API and View blueprints
│   │   ├── api.py          # REST API endpoints
│   │   └── views.py        # Frontend route rendering
│   ├── services/           # Business Logic & DB Abstraction
│   │   ├── services.py     # Facade (Switch logic)
│   │   ├── services_sql.py # MySQL Implementation
│   │   └── services_mongo.py # MongoDB Implementation
│   ├── templates/          # HTML Templates (Jinja2)
│   ├── static/             # CSS, JS, Images
│   └── models/             # SQLAlchemy Models
├── generate_vectors.py     # ETL Script (SQL -> Mongo + Embeddings)
├── main.py                 # Application Entry Point
├── config.py               # Configuration Settings
└── technical_overview.md   # Detailed Technical Report
```

## 📝 Usage Guide

1.  **Login**:
    *   **Student**: alex.student@ucms.edu:password
    *   **Instructor**: instructor1@ucms.edu:password
    *   **Admin**: admin@ucms.edu:password
2.  **Switching Databases**: Click the toggle switch in the top-right corner of the navigation bar to switch between SQL and MongoDB backends instantly.
3.  **Search**: If you're a student,try typing "Year 1 Trimester 2" in the search bar on the home page.
  Or try searching for "Web Application Development".

---

## 📄 License
This project is for educational purposes as part of the INF2003 Database Systems assignment.

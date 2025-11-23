from . import services_sql as sql_service
from . import services_mongo as mongo_service

# Global variable to track the active provider
CURRENT_PROVIDER = "sql"
_active_service = sql_service


def set_db_provider(provider_name):
    """Switches the backend service module."""
    global CURRENT_PROVIDER, _active_service

    if provider_name == "mongodb":
        CURRENT_PROVIDER = "mongodb"
        _active_service = mongo_service
        print("--> Switched to MongoDB Service")
    else:
        CURRENT_PROVIDER = "sql"
        _active_service = sql_service
        print("--> Switched to SQL Service")


# ========================================================
#  WRAPPER FUNCTIONS (Forward calls to active service)
# ========================================================


def get_module_data():
    return _active_service.get_module_data()


def get_module_details_by_id(module_id, student_id=None):
    return _active_service.get_module_details_by_id(module_id, student_id)


def create_module(data):
    return _active_service.create_module(data)


def update_module(module_id, data):
    return _active_service.update_module(module_id, data)


def delete_module(module_id):
    return _active_service.delete_module(module_id)


def get_module_details_by_ids_list(module_ids):
    return _active_service.get_module_details_by_ids_list(module_ids)



def get_all_users_detailed():
    return _active_service.get_all_users_detailed()


def create_user(data):
    return _active_service.create_user(data)


def update_user(user_id, data):
    return _active_service.update_user(user_id, data)


def delete_user(user_id):
    return _active_service.delete_user(user_id)


def get_user_full_details(user_id):
    return _active_service.get_user_full_details(user_id)


def toggle_user_status(user_id):
    return _active_service.toggle_user_status(user_id)


def enroll_student_in_module(student_id, module_id):
    return _active_service.enroll_student_in_module(student_id, module_id)


def drop_student_enrollment_module(student_id, module_id):
    return _active_service.drop_student_enrollment_module(student_id, module_id)


def get_student_enrollments(student_id):
    return _active_service.get_student_enrollments(student_id)


# --- Pass-throughs for less critical functions ---
def get_student_data():
    return _active_service.get_student_data()


def get_instructor_data():
    return _active_service.get_instructor_data()


def get_user_data():
    return _active_service.get_user_data()


def get_student_details_by_user_id(uid):
    return _active_service.get_student_details_by_user_id(uid)


def get_instructor_details_by_user_id(uid):
    return _active_service.get_instructor_details_by_user_id(uid)


def get_instructor_modules(iid):
    return _active_service.get_instructor_modules(iid)


def get_students_in_module(cid):
    return _active_service.get_students_in_module(cid)

def get_instructors_by_name(query):
    return _active_service.get_instructors_by_name(query)
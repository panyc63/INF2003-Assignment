from datetime import datetime

class Module:
    module_id: str
    module_name: str
    description: str
    credits: int
    academic_term: str
    max_capacity: int
    current_enrollment: int
    created_at: datetime
    instructor_id: int
    target_majors: str

    def __init__(self, module_id: str, module_name: str, description: str, credits: int, academic_term: str, max_capacity: int,
                 current_enrollment: int, created_at: datetime, instructor_id: int, target_majors: str):
        self.module_id = module_id
        self.module_name = module_name
        self.description = description
        self.credits = credits
        self.academic_term = academic_term
        self.max_capacity = max_capacity
        self.current_enrollment = current_enrollment
        self.created_at = created_at
        self.instructor_id = instructor_id
        self.target_majors = target_majors
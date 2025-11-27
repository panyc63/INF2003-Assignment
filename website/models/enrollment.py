from datetime import datetime

class Enrollment:
    student_id: int
    module_id: str
    enrolled_at: datetime
    final_grade: str
    status: str

    def __init__(self, student_id: int, module_id: str, enrolled_at: datetime, final_grade: str, status: str):
        self.student_id = student_id
        self.module_id = module_id
        self.enrolled_at = enrolled_at
        self.final_grade = final_grade
        self.status = status
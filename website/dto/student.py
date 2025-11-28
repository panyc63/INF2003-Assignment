class StudentEnrollmentDTO:
    module_id: str
    module_name: str
    credits: int
    academic_term: str
    status: str
    final_grade: str
    instructor_name: str

    def __init__(self, module_id: str, module_name: str, credits: int, academic_term: str, status: str,
                 final_grade: str, instructor_name: str):
        self.module_id = module_id
        self.module_name = module_name
        self.credits = credits
        self.academic_term = academic_term
        self.status = status
        self.final_grade = final_grade
        self.instructor_name = instructor_name

class StudentBasicDTO:
    student_id: int
    university_id: str
    name: str
    major: str

    def __init__(self, student_id: int, university_id: str, name: str, major: str):
        self.student_id = student_id
        self.university_id = university_id
        self.name = name
        self.major = major

class StudentDetailsByUserIdDTO:
    student_id: int
    enrollment_year: int
    major: str
    major_id: str

    def __init__(self, student_id: int, enrollment_year: int, major: str, major_id: str):
        self.student_id = student_id
        self.enrollment_year = enrollment_year
        self.major = major
        self.major_id = major_id
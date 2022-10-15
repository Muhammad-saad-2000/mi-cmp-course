class Student:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
    

class Course:
    def __init__(self, id: str, name: str, hours: int, grades = None) -> None:
        self.id = id
        self.name = name
        self.hours = hours
        self.grades = grades or {}
    
    def add_grade(self, student: Student, grade: str):
        self.grades[student.id] = grade
    
    @staticmethod
    def convert_grade_to_points(grade: str) -> float:
        return {
            "A+": 4.0,
            "A" : 4.0,
            "A-": 3.7,
            "B+": 3.5,
            "B" : 3.3,
            "B-": 3.0,
            "C+": 2.7,
            "C" : 2.5,
            "C-": 2.3,
            "D" : 2.0,
            "F" : 0.0
        }.get(grade, 0)
from .mongo_client import db

# Grades: por student_id
def get_grades_by_student(student_id):
    return list(db.grades.find({"student_id": student_id}))

# Evaluation Plans: generales, sin filtro por student_id
def get_all_evaluation_plans():
    return list(db.evaluation_plans.find())

# Comments: por student_id
def get_comments_by_student(student_id):
    return list(db.comments.find({"student_id": student_id}))

# Students: buscar por student_id o listar todos
def get_student_by_student_id(student_id):
    return db.students.find_one({"student_id": student_id})

def get_all_students():
    return list(db.students.find())

def get_dashboard_data(student_id):
    return {
        "grades": get_grades_by_student(student_id),
        "evaluation_plans": get_all_evaluation_plans(),
        "comments": get_comments_by_student(student_id),
        "student": get_student_by_student_id(student_id),
    }
    
def get_students():
    return list(db.students.find())
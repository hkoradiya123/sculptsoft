from datetime import date

from student_attendance import (
    create_student,
    create_subject,
    create_tables,
    get_attendance_percentage,
    get_student_attendance,
    get_subject_attendance,
    mark_attendance,
    update_attendance,
    get_all_students,
    get_all_subjects
    
)


def show_student_records(student_id):
    records = get_student_attendance(student_id)
    print(f"\nAttendance records for student ID {student_id}:")
    for record in records:
        status = "Present" if record.is_present else "Absent"
        print(
            f"Date: {record.attendance_date}, "
            f"Subject ID: {record.subject_id}, "
            f"Status: {status}"
        )


def show_subject_records(subject_id, attendance_date=None):
    records = get_subject_attendance(subject_id, attendance_date)
    print(f"\nAttendance records for subject ID {subject_id}:")
    for record in records:
        status = "Present" if record.is_present else "Absent"
        print(
            f"Date: {record.attendance_date}, "
            f"Student ID: {record.student_id}, "
            f"Status: {status}"
        )
        
def get_student():
    result_students = get_all_students()
    for student in result_students:
        print(f"Student ID: {student.id}, Name: {student.name}, Roll Number: {student.roll_no}")
    
def get_subject():
    result_subjects = get_all_subjects()
    for subject in result_subjects:
        print(f"Subject ID: {subject.id}, Name: {subject.name}")
    
    




if __name__ == "__main__":
    
    get_student()
    get_subject()

    # student1 = create_student("axit", "S001")
    # student2 = create_student("bhola", "S002")

    # subject1 = create_subject("Mathematics")
    # subject2 = create_subject("Science")

    # mark_attendance(student1.id, subject1.id, True)
    # mark_attendance(student1.id, subject2.id, False)
    # mark_attendance(student2.id, subject1.id, True)
    # mark_attendance(student2.id, subject2.id, True)


    # show_student_records(student1.id)
    # show_student_records(student2.id)

    # show_subject_records(subject1.id)
    # show_subject_records(subject2.id)

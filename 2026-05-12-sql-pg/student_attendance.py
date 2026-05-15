from datetime import date

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from code import Base, SessionLocal, engine


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    roll_no = Column(String(30), unique=True, nullable=False, index=True)

    attendance_records = relationship(
        "Attendance",
        back_populates="student",
        cascade="all, delete-orphan",
    )


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    attendance_records = relationship(
        "Attendance",
        back_populates="subject",
        cascade="all, delete-orphan",
    )


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    attendance_date = Column(Date, nullable=False, default=date.today)
    is_present = Column(Boolean, nullable=False)

    student = relationship("Student", back_populates="attendance_records")
    subject = relationship("Subject", back_populates="attendance_records")

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "subject_id",
            "attendance_date",
            name="uq_student_subject_attendance_date",
        ),
    )


def create_tables():
    Base.metadata.create_all(bind=engine)


def create_student(name: str, roll_no: str):
    db = SessionLocal()
    try:
        student = Student(name=name, roll_no=roll_no)
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    finally:
        db.close()


def create_subject(name: str):
    db = SessionLocal()
    try:
        subject = Subject(name=name)
        db.add(subject)
        db.commit()
        db.refresh(subject)
        return subject
    finally:
        db.close()


def mark_attendance(
    student_id: int,
    subject_id: int,
    is_present: bool,
    attendance_date: date | None = None,
):
    db = SessionLocal()
    try:
        record = Attendance(
            student_id=student_id,
            subject_id=subject_id,
            attendance_date=attendance_date or date.today(),
            is_present=is_present,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    finally:
        db.close()


def update_attendance(
    student_id: int,
    subject_id: int,
    is_present: bool,
    attendance_date: date | None = None,
):
    db = SessionLocal()
    try:
        record_date = attendance_date or date.today()
        record = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student_id,
                Attendance.subject_id == subject_id,
                Attendance.attendance_date == record_date,
            )
            .first()
        )
        if record is None:
            return None

        record.is_present = is_present
        db.commit()
        db.refresh(record)
        return record
    finally:
        db.close()


def get_student_attendance(student_id: int):
    db = SessionLocal()
    try:
        return (
            db.query(Attendance)
            .filter(Attendance.student_id == student_id)
            .order_by(Attendance.attendance_date.desc())
            .all()
        )
    finally:
        db.close()


def get_subject_attendance(subject_id: int, attendance_date: date | None = None):
    db = SessionLocal()
    try:
        query = db.query(Attendance).filter(Attendance.subject_id == subject_id)
        if attendance_date is not None:
            query = query.filter(Attendance.attendance_date == attendance_date)
        return query.order_by(Attendance.attendance_date.desc()).all()
    finally:
        db.close()


def get_attendance_percentage(student_id: int, subject_id: int):
    db = SessionLocal()
    try:
        records = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student_id,
                Attendance.subject_id == subject_id,
            )
            .all()
        )
        if not records:
            return 0

        present_count = sum(1 for record in records if record.is_present)
        return (present_count / len(records)) * 100
    finally:
        db.close()
def get_all_students():
    db = SessionLocal()
    try:
        return db.query(Student).all()
    finally:
        db.close()
        
def get_all_subjects():
    db = SessionLocal()
    try:
        return db.query(Subject).all()
    finally:
        db.close()

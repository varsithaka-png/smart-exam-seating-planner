
from sqlalchemy import (
    Column, Integer, String, Text, Date, Time, DateTime,
    Boolean, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    register_number = Column(String(30), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    year = Column(Integer)
    email = Column(String(100))


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String(30), unique=True)
    subject_name = Column(String(150), nullable=False)


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id"),
    )


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    duration_minutes = Column(Integer)
    exam_type = Column(String(50))


class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    session_name = Column(String(50))
    start_time = Column(Time)
    end_time = Column(Time)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    room_number = Column(String(30), unique=True, nullable=False)
    building = Column(String(100))
    rows = Column(Integer)
    seat_columns = Column(Integer)
    capacity = Column(Integer, nullable=False)


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(30), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    email = Column(String(100))


class TeacherUnavailability(Base):
    __tablename__ = "teacher_unavailability"

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=False)
    reason = Column(String(255))

    __table_args__ = (
        UniqueConstraint("teacher_id", "session_id"),
    )


class SeatAssignment(Base):
    __tablename__ = "seat_assignments"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    seat_number = Column(String(20), nullable=False)
    row_number = Column(Integer)
    column_number = Column(Integer)

    __table_args__ = (
        UniqueConstraint("session_id", "student_id"),
        UniqueConstraint("session_id", "room_id", "seat_number"),
    )


class DutyAssignment(Base):
    __tablename__ = "duty_assignments"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    role = Column(String(30), nullable=False)
    is_replacement = Column(Boolean, default=False)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    status = Column(String(20), nullable=False)
    marked_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("session_id", "student_id"),
    )


class InvigilatorAttendance(Base):
    __tablename__ = "invigilator_attendance"

    id = Column(Integer, primary_key=True)
    duty_assignment_id = Column(
        Integer, ForeignKey("duty_assignments.id"), nullable=False
    )
    status = Column(String(20), nullable=False)
    marked_at = Column(DateTime, default=datetime.utcnow)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    reported_by = Column(Integer, ForeignKey("teachers.id"))
    incident_type = Column(String(100))
    description = Column(Text)
    reported_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

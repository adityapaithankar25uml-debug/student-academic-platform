from flask import Blueprint, jsonify, request

from app.services import (
    create_course,
    create_faculty,
    create_grade,
    create_student,
    calculate_gpa,
    enroll_student,
    get_courses,
    get_enrollments,
    get_faculty,
    get_grades,
    get_students,
)


api = Blueprint("api", __name__)


@api.post("/students")
def add_student():
    data = request.get_json(silent=True) or {}

    required_fields = ["name", "email", "semester"]

    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "name, email and semester are required"
        }), 400

    try:
        student = create_student(
            data["name"],
            data["email"],
            int(data["semester"]),
        )

        return jsonify(student), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 400


@api.get("/students")
def list_students():
    return jsonify(get_students())


@api.post("/courses")
def add_course():
    data = request.get_json(silent=True) or {}

    required_fields = ["code", "name", "credits"]

    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "code, name and credits are required"
        }), 400

    try:
        course = create_course(
            data["code"],
            data["name"],
            int(data["credits"]),
        )

        return jsonify(course), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 400


@api.get("/courses")
def list_courses():
    return jsonify(get_courses())


@api.post("/faculty")
def add_faculty():
    data = request.get_json(silent=True) or {}

    required_fields = ["name", "email"]

    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "name and email are required"
        }), 400

    try:
        faculty = create_faculty(
            data["name"],
            data["email"],
        )

        return jsonify(faculty), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 400


@api.get("/faculty")
def list_faculty():
    return jsonify(get_faculty())


@api.post("/enrollments")
def add_enrollment():
    data = request.get_json(silent=True) or {}

    required_fields = ["student_id", "course_id", "semester"]

    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "student_id, course_id and semester are required"
        }), 400

    try:
        enrollment = enroll_student(
            int(data["student_id"]),
            int(data["course_id"]),
            int(data["semester"]),
        )

        return jsonify(enrollment), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 400


@api.get("/enrollments")
def list_enrollments():
    return jsonify(get_enrollments())


@api.post("/grades")
def add_grade():
    data = request.get_json(silent=True) or {}

    required_fields = ["student_id", "course_id", "grade"]

    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "student_id, course_id and grade are required"
        }), 400

    try:
        grade = create_grade(
            int(data["student_id"]),
            int(data["course_id"]),
            data["grade"],
        )

        return jsonify(grade), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 400


@api.get("/grades")
def list_grades():
    return jsonify(get_grades())


@api.get("/students/<int:student_id>/gpa")
def student_gpa(student_id):
    try:
        gpa = calculate_gpa(student_id)

        return jsonify({
            "student_id": student_id,
            "gpa": gpa,
        })

    except Exception as error:
        return jsonify({"error": str(error)}), 400

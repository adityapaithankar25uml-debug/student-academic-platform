from database.db import get_connection


def create_student(name, email, semester):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO students (name, email, semester)
            VALUES (?, ?, ?)
            """,
            (name, email, semester),
        )
        connection.commit()

        return {
            "id": cursor.lastrowid,
            "name": name,
            "email": email,
            "semester": semester,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_students():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT id, name, email, semester
        FROM students
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def create_course(code, name, credits):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO courses (code, name, credits)
            VALUES (?, ?, ?)
            """,
            (code, name, credits),
        )
        connection.commit()

        return {
            "id": cursor.lastrowid,
            "code": code,
            "name": name,
            "credits": credits,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_courses():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT id, code, name, credits
        FROM courses
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def create_faculty(name, email):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO faculty (name, email)
            VALUES (?, ?)
            """,
            (name, email),
        )
        connection.commit()

        return {
            "id": cursor.lastrowid,
            "name": name,
            "email": email,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_faculty():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT id, name, email
        FROM faculty
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def enroll_student(student_id, course_id, semester):
    connection = get_connection()

    try:
        # Check whether the student exists.
        student = connection.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()

        if student is None:
            raise ValueError("Student not found")

        # Check whether the course exists.
        course = connection.execute(
            "SELECT id, credits FROM courses WHERE id = ?",
            (course_id,),
        ).fetchone()

        if course is None:
            raise ValueError("Course not found")

        # Prevent duplicate enrollment in the same course and semester.
        existing = connection.execute(
            """
            SELECT id
            FROM enrollments
            WHERE student_id = ?
              AND course_id = ?
              AND semester = ?
            """,
            (student_id, course_id, semester),
        ).fetchone()

        if existing is not None:
            raise ValueError(
                "Enrollment conflict: student is already enrolled "
                "in this course for this semester"
            )

        # Calculate current semester credits.
        current = connection.execute(
            """
            SELECT COALESCE(SUM(c.credits), 0) AS total_credits
            FROM enrollments e
            JOIN courses c ON c.id = e.course_id
            WHERE e.student_id = ?
              AND e.semester = ?
            """,
            (student_id, semester),
        ).fetchone()

        current_credits = current["total_credits"]
        new_total = current_credits + course["credits"]

        # Assignment requirement: maximum 18 credits per semester.
        if new_total > 18:
            raise ValueError(
                f"Credit limit exceeded: current={current_credits}, "
                f"course={course['credits']}, maximum=18"
            )

        cursor = connection.execute(
            """
            INSERT INTO enrollments
                (student_id, course_id, semester)
            VALUES (?, ?, ?)
            """,
            (student_id, course_id, semester),
        )

        connection.commit()

        return {
            "id": cursor.lastrowid,
            "student_id": student_id,
            "course_id": course_id,
            "semester": semester,
            "total_credits": new_total,
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_enrollments():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            e.id,
            e.student_id,
            s.name AS student_name,
            e.course_id,
            c.code AS course_code,
            c.name AS course_name,
            c.credits,
            e.semester
        FROM enrollments e
        JOIN students s ON s.id = e.student_id
        JOIN courses c ON c.id = e.course_id
        ORDER BY e.id
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


GRADE_POINTS = {
    "A": 10,
    "B": 8,
    "C": 6,
    "D": 5,
    "E": 4,
    "F": 0,
}


def create_grade(student_id, course_id, grade):
    grade = grade.upper()

    if grade not in GRADE_POINTS:
        raise ValueError("Grade must be one of A, B, C, D, E or F")

    connection = get_connection()

    try:
        student = connection.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()

        if student is None:
            raise ValueError("Student not found")

        course = connection.execute(
            "SELECT id FROM courses WHERE id = ?",
            (course_id,),
        ).fetchone()

        if course is None:
            raise ValueError("Course not found")

        enrollment = connection.execute(
            """
            SELECT id
            FROM enrollments
            WHERE student_id = ?
              AND course_id = ?
            """,
            (student_id, course_id),
        ).fetchone()

        if enrollment is None:
            raise ValueError(
                "Grade cannot be assigned before course enrollment"
            )

        existing = connection.execute(
            """
            SELECT id
            FROM grades
            WHERE student_id = ?
              AND course_id = ?
            """,
            (student_id, course_id),
        ).fetchone()

        if existing is not None:
            raise ValueError(
                "Grade already exists for this student and course"
            )

        cursor = connection.execute(
            """
            INSERT INTO grades (student_id, course_id, grade)
            VALUES (?, ?, ?)
            """,
            (student_id, course_id, grade),
        )

        connection.commit()

        return {
            "id": cursor.lastrowid,
            "student_id": student_id,
            "course_id": course_id,
            "grade": grade,
            "grade_points": GRADE_POINTS[grade],
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_grades():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            g.id,
            g.student_id,
            s.name AS student_name,
            g.course_id,
            c.code AS course_code,
            c.name AS course_name,
            c.credits,
            g.grade
        FROM grades g
        JOIN students s ON s.id = g.student_id
        JOIN courses c ON c.id = g.course_id
        ORDER BY g.id
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def calculate_gpa(student_id):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT c.credits, g.grade
        FROM grades g
        JOIN courses c ON c.id = g.course_id
        WHERE g.student_id = ?
        """,
        (student_id,),
    ).fetchall()

    connection.close()

    if not rows:
        return 0.0

    total_points = sum(
        GRADE_POINTS[row["grade"]] * row["credits"]
        for row in rows
    )

    total_credits = sum(row["credits"] for row in rows)

    return round(total_points / total_credits, 2)

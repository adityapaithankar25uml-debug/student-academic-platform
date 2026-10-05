def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_create_student(client):
    response = client.post(
        "/api/students",
        json={
            "name": "Test Student",
            "email": "test@example.com",
            "semester": 1,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["name"] == "Test Student"
    assert data["email"] == "test@example.com"
    assert data["semester"] == 1


def test_create_course(client):
    response = client.post(
        "/api/courses",
        json={
            "code": "CS101",
            "name": "Python Programming",
            "credits": 4,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["code"] == "CS101"
    assert data["credits"] == 4


def test_student_enrollment(client):
    student = client.post(
        "/api/students",
        json={
            "name": "Test Student",
            "email": "student@example.com",
            "semester": 1,
        },
    ).get_json()

    course = client.post(
        "/api/courses",
        json={
            "code": "CS101",
            "name": "Python Programming",
            "credits": 4,
        },
    ).get_json()

    response = client.post(
        "/api/enrollments",
        json={
            "student_id": student["id"],
            "course_id": course["id"],
            "semester": 1,
        },
    )

    assert response.status_code == 201
    assert response.get_json()["total_credits"] == 4


def test_duplicate_enrollment_is_rejected(client):
    student = client.post(
        "/api/students",
        json={
            "name": "Test Student",
            "email": "duplicate@example.com",
            "semester": 1,
        },
    ).get_json()

    course = client.post(
        "/api/courses",
        json={
            "code": "CS101",
            "name": "Python Programming",
            "credits": 4,
        },
    ).get_json()

    enrollment = {
        "student_id": student["id"],
        "course_id": course["id"],
        "semester": 1,
    }

    first = client.post("/api/enrollments", json=enrollment)
    second = client.post("/api/enrollments", json=enrollment)

    assert first.status_code == 201
    assert second.status_code == 400
    assert "Enrollment conflict" in second.get_json()["error"]


def test_18_credit_limit_is_enforced(client):
    student = client.post(
        "/api/students",
        json={
            "name": "Credit Limit Student",
            "email": "credits@example.com",
            "semester": 1,
        },
    ).get_json()

    courses = []

    for index, credits in enumerate([4, 5, 5, 5], start=1):
        course = client.post(
            "/api/courses",
            json={
                "code": f"CS10{index}",
                "name": f"Course {index}",
                "credits": credits,
            },
        ).get_json()

        courses.append(course)

    for course in courses[:3]:
        response = client.post(
            "/api/enrollments",
            json={
                "student_id": student["id"],
                "course_id": course["id"],
                "semester": 1,
            },
        )

        assert response.status_code == 201

    response = client.post(
        "/api/enrollments",
        json={
            "student_id": student["id"],
            "course_id": courses[3]["id"],
            "semester": 1,
        },
    )

    assert response.status_code == 400
    assert "Credit limit exceeded" in response.get_json()["error"]


def test_gpa_calculation(client):
    student = client.post(
        "/api/students",
        json={
            "name": "GPA Student",
            "email": "gpa@example.com",
            "semester": 1,
        },
    ).get_json()

    course_data = [
        ("CS101", "Python Programming", 4, "A"),
        ("CS201", "Data Structures", 5, "B"),
        ("CS202", "Database Systems", 5, "C"),
    ]

    for code, name, credits, grade in course_data:
        course = client.post(
            "/api/courses",
            json={
                "code": code,
                "name": name,
                "credits": credits,
            },
        ).get_json()

        client.post(
            "/api/enrollments",
            json={
                "student_id": student["id"],
                "course_id": course["id"],
                "semester": 1,
            },
        )

        grade_response = client.post(
            "/api/grades",
            json={
                "student_id": student["id"],
                "course_id": course["id"],
                "grade": grade,
            },
        )

        assert grade_response.status_code == 201

    response = client.get(
        f"/api/students/{student['id']}/gpa"
    )

    assert response.status_code == 200
    assert response.get_json()["gpa"] == 7.86

import pytest
import json
from django.test import Client
from student_management_app.models import Subjects, Students, SessionYearModel, CustomUser, Courses


@pytest.mark.django_db
class TestGetStudentsView:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client()

        # Tạo course
        self.course = Courses.objects.create(course_name="Test Course")

        # Tạo session
        self.session_year = SessionYearModel.objects.create(
            session_start_year="2023-01-01",
            session_end_year="2023-12-31"
        )

        # Tạo staff (vì Subjects cần staff_id)
        self.staff_user = CustomUser.objects.create_user(
            username="staff1",
            password="pass123",
            user_type=2,
            first_name="Staff",
            last_name="User",
            email="staff@example.com"
        )

        # Tạo subject
        self.subject = Subjects.objects.create(
            subject_name="Math",
            course_id=self.course,
            staff_id=self.staff_user
        )

        # Tạo student
        self.student_user = CustomUser.objects.create_user(
            username="student1",
            password="pass123",
            user_type=3,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        self.student = Students.objects.get(admin=self.student_user)
        self.student.course_id = self.course
        self.student.session_year_id = self.session_year
        self.student.save()

    def test_get_students_success(self):
        response = self.client.post(
            "/get_students/",
            data={"subject": self.subject.id, "session_year": self.session_year.id}
        )
        assert response.status_code == 200
        result = json.loads(response.content)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "John Doe"

    def test_get_students_no_students(self):
        self.student.delete()
        response = self.client.post(
            "/get_students/",
            data={"subject": self.subject.id, "session_year": self.session_year.id}
        )
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result == []

    def test_get_students_invalid_subject_id(self):
        response = self.client.post(
            "/get_students/",
            data={"subject": 9999, "session_year": self.session_year.id}
        )
        assert response.status_code == 500

    def test_get_students_invalid_session_year_id(self):
        response = self.client.post(
            "/get_students/",
            data={"subject": self.subject.id, "session_year": 9999}
        )
        assert response.status_code == 500

    def test_get_students_missing_parameters(self):
        response = self.client.post("/get_students/", data={})
        assert response.status_code == 500

        
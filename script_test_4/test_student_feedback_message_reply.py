import pytest
from django.test import Client, override_settings
from django.urls import reverse
from student_management_app.models import CustomUser, Courses, SessionYearModel, Students, FeedbackStudent
from student_management_app.EmailBackEnd import EmailBackEnd

@pytest.mark.django_db
class TestFeedbackStudent:

    def setup_method(self):
        # Khởi tạo client và URL để gọi endpoint phản hồi feedback
        self.client = Client()
        self.url = reverse("student_feedback_message_reply")
        self.backend = EmailBackEnd()

        # Tạo một tài khoản admin để xác thực
        self.admin = CustomUser.objects.create_user(
            username="admin002",
            password="admin0022",
            email="adminw@gmail.com",
            first_name="first_name",
            last_name="last_name",
            user_type=1  # 1: Admin
        )

        # Xác thực admin bằng EmailBackEnd
        self.user = self.backend.authenticate(
            username="adminw@gmail.com",
            password="admin0022"
        )

        # Tạo course và session để phục vụ việc tạo student
        course = Courses.objects.create(course_name="Computer Science")
        session = SessionYearModel.objects.create(
            session_start_year="2024-01-01",
            session_end_year="2025-01-01"
        )

        # Tạo một student user
        self.student = CustomUser.objects.create_user(
            username="joh2342andor123",
            password="securepassword123",
            email="john23423andor@example.com",
            first_name="first_name",
            last_name="last_name",
            user_type=3  # 3: Student
        )

        # Cập nhật thông tin chi tiết cho student
        self.student.students.address = "Hà Nội"
        self.student.students.course_id = Courses.objects.get(id=course.id)
        self.student.students.session_year_id = SessionYearModel.objects.get(id=session.id)
        self.student.students.gender = "Male"
        self.student.students.save()

        # Tạo feedback của student
        student_obj = Students.objects.get(admin=self.student.id)
        self.feedback = FeedbackStudent(student_id=student_obj, feedback="Heloo tess", feedback_reply="")
        self.feedback.save()

    def test_valid_feedback_reply(self):
        """
        Test case 1: gửi phản hồi thành công cho feedback hợp lệ.
        Mong đợi: status_code = 200, nội dung response là "True",
        và feedback_reply được cập nhật chính xác trong database.
        """
        with override_settings(MIDDLEWARE=[]):
            response = self.client.post(self.url, {
                "id": self.feedback.id,
                "reply": "Thank you!"
            })
        assert response.status_code == 200
        assert response.content == b"True"
        self.feedback.refresh_from_db()
        assert self.feedback.feedback_reply == "Thank you!"

    def test_invalid_feedback_id(self):
        """
        Test case 2: gửi phản hồi với ID không tồn tại trong database.
        Mong đợi: status_code = 200, nội dung response là "False".
        """
        with override_settings(MIDDLEWARE=[]):
            response = self.client.post(self.url, {
                "id": 99999,
                "reply": "Some reply"
            })
        assert response.status_code == 200
        assert response.content == b"False"

    def test_missing_post_data(self):
        """
        Test case 3: gửi request POST nhưng thiếu cả hai tham số 'id' và 'reply'.
        Mong đợi: status_code = 200, nội dung response là "False".
        """
        with override_settings(MIDDLEWARE=[]):
            response = self.client.post(self.url, {})  # không gửi id và reply
        assert response.status_code == 200
        assert response.content == b"False"

    def test_invalid_post_method(self):
        """
        Test case 4: gửi request bằng phương thức GET thay vì POST.
        Mong đợi: status_code = 405 vì không hỗ trợ phương thức GET.
        """
        with override_settings(MIDDLEWARE=[]):
            response = self.client.get(self.url)
        assert response.status_code == 405

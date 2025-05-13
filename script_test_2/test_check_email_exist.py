import pytest
from django.urls import reverse
from django.test import Client, override_settings
from student_management_app.models import CustomUser

@pytest.mark.django_db
class TestCheckEmailExistView:

    def setup_method(self):
        self.client = Client()
        # URL được ánh xạ từ name="check_email_exist" trong urls.py
        self.url = reverse("check_email_exist")
        self.test_email = "test@example.com"

        # Tạo 1 user mẫu để test trường hợp email tồn tại
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email=self.test_email,
            password="securepassword",
            first_name="first_name",
            last_name="last_name",
            user_type=2
        )

    def test_email_exists_returns_true(self):
        # Test case 1: Email tồn tại trong database
        # Mong đợi: trả về "True"
        with override_settings(MIDDLEWARE=[]):
            response = self.client.post(self.url, data={"email": self.test_email})
        assert response.status_code == 200
        assert response.content == b"True"

    def test_email_not_exists_returns_false(self):
        # Test case 2: Email không tồn tại trong database
        # Mong đợi: trả về "False"
        with override_settings(MIDDLEWARE=[]):
            response = self.client.post(self.url, data={"email": "notfound@example.com"})
        assert response.status_code == 200
        assert response.content == b"False"

    def test_no_email_provided_returns_false(self):
        # Test case 3: Không truyền email trong request
        # Mong đợi: lỗi mã 400 vì request không hợp lệ (400) vì không có email
        with override_settings(MIDDLEWARE=[]):
            response = self.client.post(self.url, data={})
        assert response.status_code == 400
        assert response.content == b"False"

    def test_get_method_returns_405(self):
        # Test case 4: Gửi request bằng phương thức GET thay vì POST
        # Mong đợi: mã lỗi 405 vì phương thức không được cho phép
        with override_settings(MIDDLEWARE=[]):
            response = self.client.get(self.url)
        assert response.status_code == 405

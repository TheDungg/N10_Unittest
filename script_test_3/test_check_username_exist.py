import pytest
from django.urls import reverse
from django.test import Client, override_settings
from student_management_app.models import CustomUser

@pytest.mark.django_db
class TestCheckUsernameExistView:

    def setup_method(self):
        self.client = Client()
        # URL được ánh xạ từ name="check_username_exist" trong urls.py
        self.url = reverse("check_username_exist")
        self.test_username = "hellllio"

        # Tạo 1 user mẫu để test trường hợp username tồn tại
        self.user = CustomUser.objects.create_user(
            username=self.test_username,
            email="hello1@gmail.com",
            password="securepassword",
            first_name="first_name",
            last_name="last_name",
            user_type=2
        )

    def test_username_exists_returns_true(self):
        """
        Test case 1: Username tồn tại trong database
        Mong đợi: trả về "True"
        """
        with override_settings(MIDDLEWARE=[]):
            response = self.client.post(
                self.url,
                data={"username": self.test_username}
            )
        assert response.status_code == 200
        assert response.content == b"True"

    def test_username_not_exists_returns_false(self):
        """
        Test case 2: Username không tồn tại trong database
        Mong đợi: trả về "False"
        """
        with override_settings(MIDDLEWARE=[]):
            response = self.client.post(
                self.url,
                data={"username": "notfound"}
            )
        assert response.status_code == 200
        assert response.content == b"False"

    def test_no_username_provided_returns_false(self):
        """
        Test case 3: Không truyền username trong request
        Mong đợi: Hàm trả ra lỗi request không hợp lệ (400) vì không có username
        """
        with override_settings(MIDDLEWARE=[]):
            response = self.client.post(self.url, data={})
        assert response.status_code == 400
        assert response.content == b"False"

    def test_get_method_returns_405(self):
        """
        Test case 4: Gửi request bằng phương thức GET thay vì POST
        Mong đợi: Hàm trả ra lỗi phương thức không được cho phép (405)
        """
        with override_settings(MIDDLEWARE=[]):
            response = self.client.get(self.url)
        assert response.status_code == 405

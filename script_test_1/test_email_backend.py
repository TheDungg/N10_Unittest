from student_management_app.EmailBackEnd import EmailBackEnd
from student_management_app.models import CustomUser

class TestEmailBackend:
    def setup_method(self):
        # Tạo tài khoản người dùng demo test
        self.backend = EmailBackEnd()
        self.username = "test@example.com"
        self.email = "test@example.com"
        self.password = "securepassword"
        self.wrong_password = "wrongpassword"

        self.user = CustomUser.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email,
            first_name="first_name",
            last_name="last_name",
            user_type=2
        )

    # Test case 1: user tồn tại và mật khẩu đúng
    def test_authenticate_success(self):
        user = self.backend.authenticate(
            username=self.email,
            password=self.password
        )

        # Mong đợi: trả về user object (khác None)
        assert user is not None

        # Mong đợi: user trả về có đúng email đã tạo ở trên
        assert user.email == self.email

    # Test case 2: user tồn tại nhưng mật khẩu sai
    def test_authenticate_wrong_password(self):
        user = self.backend.authenticate(
            username=self.email,
            password=self.wrong_password
        )

        # Mong đợi: trả về None vì mật khẩu không đúng
        assert user is None

    # Test case 3: user không tồn tại trong hệ thống
    def test_authenticate_user_not_exist(self):
        user = self.backend.authenticate(
            username="nonexistent@example.com",
            password="any"
        )

        # Mong đợi: trả về None vì không tìm thấy user với email này
        assert user is None

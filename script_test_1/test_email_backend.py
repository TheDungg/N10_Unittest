import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from student_management_app.EmailBackEnd import EmailBackEnd

User = get_user_model()

class EmailBackEndTestCase(TestCase):
    """
    Bộ kiểm thử cho lớp xác thực EmailBackEnd.
    """

    def setUp(self):
        """
        Thiết lập một người dùng thử nghiệm và khởi tạo lớp EmailBackEnd.
        """
        self.backend = EmailBackEnd()
        self.user_email = "testuser@example.com"
        self.user_password = "testpassword123"
        # Tạo người dùng mẫu với email và mật khẩu để kiểm thử xác thực
        self.user = User.objects.create_user(
            email=self.user_email,
            password=self.user_password,
            username="testuser"
        )

    def test_authenticate_with_correct_email_and_password(self):
        """
        Kiểm tra xác thực thành công khi nhập đúng email và mật khẩu.
        """
        user = self.backend.authenticate(username=self.user_email, password=self.user_password)
        self.assertIsNotNone(user, "Xác thực phải thành công khi thông tin hợp lệ.")
        self.assertEqual(user.email, self.user_email, "Email người dùng trả về phải trùng với email đã dùng để đăng nhập.")

    def test_authenticate_with_wrong_email(self):
        """
        Kiểm tra xác thực thất bại khi email không đúng.
        """
        user = self.backend.authenticate(username="wrong@example.com", password=self.user_password)
        self.assertIsNone(user, "Xác thực phải thất bại khi email không đúng.")

    def test_authenticate_with_wrong_password(self):
        """
        Kiểm tra xác thực thất bại khi mật khẩu không đúng.
        """
        user = self.backend.authenticate(username=self.user_email, password="wrongpassword")
        self.assertIsNone(user, "Xác thực phải thất bại khi mật khẩu sai.")

    def test_authenticate_with_no_email(self):
        """
        Kiểm tra xác thực thất bại khi không truyền email.
        """
        user = self.backend.authenticate(username=None, password=self.user_password)
        self.assertIsNone(user, "Xác thực phải thất bại khi email bị thiếu.")

    def test_authenticate_with_no_password(self):
        """
        Kiểm tra xác thực thất bại khi không truyền mật khẩu.
        """
        user = self.backend.authenticate(username=self.user_email, password=None)
        self.assertIsNone(user, "Xác thực phải thất bại khi không có mật khẩu.")

    def test_authenticate_with_nonexistent_user(self):
        """
        Kiểm tra xác thực thất bại khi người dùng không tồn tại.
        """
        user = self.backend.authenticate(username="abcdef", password="wrongpassword")
        self.assertIsNone(user, "Xác thực phải thất bại nếu người dùng không tồn tại.")

    def test_authenticate_with_empty_credentials(self):
        """
        Kiểm tra xác thực thất bại khi cả email và mật khẩu là chuỗi rỗng.
        """
        user = self.backend.authenticate(username="", password="")
        self.assertIsNone(user, "Xác thực phải thất bại khi email và mật khẩu rỗng.")

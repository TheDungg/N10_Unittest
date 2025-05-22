import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from student_management_app.EmailBackEnd import EmailBackEnd

User = get_user_model()

class EmailBackEndTestCase(TestCase):
    """
    Test suite for the EmailBackEnd authentication backend.
    """

    def setUp(self):
        """
        Set up a test user and initialize the EmailBackEnd instance.
        """
        self.backend = EmailBackEnd()
        self.user_email = "testuser@example.com"
        self.user_password = "testpassword123"
        # Create a user with email and password for authentication tests
        self.user = User.objects.create_user(
            email=self.user_email,
            password=self.user_password,
            username="testuser"
        )

    def test_authenticate_with_correct_email_and_password(self):
        """
        Test that authenticate returns a user object when provided correct email and password.
        """
        user = self.backend.authenticate(username=self.user_email, password=self.user_password)
        self.assertIsNotNone(user, "Authentication should succeed with valid credentials.")
        self.assertEqual(user.email, self.user_email, "Returned user email should match the one used for login.")

    def test_authenticate_with_wrong_email(self):
        """
        Test that authenticate returns None when the email is incorrect.
        """
        user = self.backend.authenticate(username="wrong@example.com", password=self.user_password)
        self.assertIsNone(user, "Authentication should fail with an incorrect email.")

    def test_authenticate_with_wrong_password(self):
        """
        Test that authenticate returns None when the password is incorrect.
        """
        user = self.backend.authenticate(username=self.user_email, password="wrongpassword")
        self.assertIsNone(user, "Authentication should fail with an incorrect password.")

    def test_authenticate_with_no_email(self):
        """
        Test that authenticate returns None when no email is provided.
        """
        user = self.backend.authenticate(username=None, password=self.user_password)
        self.assertIsNone(user, "Authentication should fail when the email is None.")

    def test_authenticate_with_no_password(self):
        """
        Test that authenticate returns None when no password is provided.
        """
        user = self.backend.authenticate(username=self.user_email, password=None)
        self.assertIsNone(user, "Authentication should fail when the password is None.")
        
    def test_authenticate_with_nonexistent_user(self):
        """
        Test that authenticate returns None when the user does not exist.
        """
        user = self.backend.authenticate(username="abcdef", password="wrongpassword")
        self.assertIsNone(user, "Authentication should fail for a nonexistent user.")
        
    def test_authenticate_with_empty_credentials(self):
        """
        Test that authenticate returns None when empty strings are provided for both username and password.
        """
        user = self.backend.authenticate(username="", password="")
        self.assertIsNone(user, "Authentication should fail when credentials are empty strings.")

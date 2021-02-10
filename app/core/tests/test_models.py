from django.test import TestCase
from django.contrib.auth import get_user_model


class TestModel(TestCase):

    def test_create_user_with_email_successfully(self):
        """Test create user with only email and password"""
        email = 'salman@gmail.com'
        password = 'something1234'
        user = get_user_model().objects.create_user(email=email,
                                                    password=password)
        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(password))

    def test_make_new_user_email_normalized(self):
        """Test make new user email normalized"""
        email = "salman@GMAIL.COME"
        user = get_user_model().objects.create_user(email=email,
                                                    password="test1234")

        self.assertEqual(user.email, email.lower())

    def test_make_user_invalid_email(self):
        """Test raise error if email is not valid"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None,
                                                 password="test1234")

    def test_create_super_user(self):
        "Test creating a new super user"
        user = get_user_model().objects.create_superuser(
            email="jamshid@gmail.com",
            password="test1234")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

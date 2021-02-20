from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Tag, Ingredient


def sample_user(email='test@gmail.com', password='test1234'):
    """Create sample user"""
    return get_user_model().objects.create_user(email=email, password=password)


class TestModel(TestCase):

    def test_create_user_with_email_successfully(self):
        """Test create user with only email and password"""
        email = 'salman@gmail.com'
        password = 'something1234'
        user = get_user_model().objects.create_user(email=email,
                                                    password=password, )
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

    def test_tag_is_string(self):
        """Test that tag has a good string representation"""
        tag = Tag.objects.create(
            user=sample_user(),
            name="Vegan")

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_is_string(self):
        """Test that ingredient has a good string representation"""
        ingredient = Ingredient.objects.create(
            user=sample_user(),
            name='paper'
        )

        self.assertEqual(str(ingredient), ingredient.name)

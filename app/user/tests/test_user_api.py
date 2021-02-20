from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITest(TestCase):
    """Test the user API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_valid_user_success(self):
        """Test that user validated and created successfully"""
        payload = {
            'email': "salman@gmail.com",
            'password': 'test1234',
            'name': "Salman Barani"
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test that user already exists"""
        payload = {"email": "jasom@gmail.com", "password": "tests1234",
                   "name": "Jasom Barani"}

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password(self):
        """Test for short passwords < 5 characters"""
        payload = {'email': "salman@gmail.com", "password": 'pw',
                   "name": "Salman Barani"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            **res.data
        ).exists()
        self.assertFalse(user_exist)

    def test_tokes_is_created(self):
        """Test that token is returned after logging in"""
        payload = {'email': "salman@gmail.com", 'password': 'test1234'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_invalid_credential(self):
        """Test the token is not created when credentials is invalid"""
        payload = {'email': "salman@gmail.com", 'password': 'test1234'}
        wrong_payload = {'email': "salman@gmail.com", 'password': 'wrong'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, wrong_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_token_without_user(self):
        """Test the token is not created when user is not created"""
        payload = {'email': "salman@gmail.com", 'password': 'test1234'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_token_missing_field(self):
        """Test the token is not created when a field is missing"""
        payload = {'email': "salman@gmail.com", 'password': 'test1234'}
        wrong_payload = {'email': "salman@gmail.com"}
        create_user(**payload)

        res = self.client.post(TOKEN_URL, wrong_payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    """Test API request for authenticated user"""

    def setUp(self):
        self.user = create_user(
            email='Salman@gmail.com',
            password='test1234',
            name='Salman Barani'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test that logged in user gets profile"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "name": self.user.name,
            "email": self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that user can't make http post request on me url"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_success(self):
        """Test that updating user works correctly"""
        payload = {'name': 'Something beautiful',
                   'password': 'something1234'}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertTrue(res.status_code, status.HTTP_200_OK)

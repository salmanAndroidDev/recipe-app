from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    default = {
        "title": "sample recipe",
        "time_minutes": 12,
        "price": 12.00
    }
    default.update(params)
    return Recipe.objects.create(user=user, **default)


class PublicAPITest(TestCase):
    """Tests that doesn't require authentication"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that any request without authentication fails"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITest(TestCase):
    """Tests that requires authentication"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='salman@gmail.com',
            password='asdf1234',
            name='Salman Barani')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test that retrieving recipes is successful"""
        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limited_to_user(self):
        """Test that requests are limited to authenticated user"""
        user2 = get_user_model().objects.create_user(
            'salman@outlook.com',
            'pass1234'
        )
        sample_recipe(user=user2, title='Stake')
        sample_recipe(self.user)

        user_recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(user_recipes, many=True)

        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

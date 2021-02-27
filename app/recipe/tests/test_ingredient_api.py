from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import IngredientSerializer
from core.models import Ingredient, Recipe

INGREDIENT_URL = reverse('recipe:ingredient-list')


def sample_user(email='salman@gmail.com', password='test1234'):
    return get_user_model().objects.create_user(
        email=email, password=password
    )


class PublicIngredientAPITest(TestCase):
    """public api test class for ingredient"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that authentication is required"""
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITest(TestCase):
    """Public api test class for ingredient"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieve ingredient list"""
        Ingredient.objects.create(name='3 eggs', user=self.user)
        Ingredient.objects.create(name='oil', user=self.user)
        Ingredient.objects.create(name='meat', user=self.user)

        serializer = IngredientSerializer(
            Ingredient.objects.all().order_by('-name'), many=True)

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_user_limit(self):
        """Test that ingredient is limited to authenticated user"""
        ingredient = Ingredient.objects.create(name='3 eggs',
                                               user=self.user)
        another_user = sample_user(email='alaki@gmail.com')
        Ingredient.objects.create(name='9 breads',
                                  user=another_user)

        res = self.client.get(INGREDIENT_URL, )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test that creating ingredient was successful"""
        payload = {"name": "salt"}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        ingredient_exists = Ingredient.objects.filter(name=payload['name'],
                                                      user=self.user,
                                                      ).exists()
        self.assertTrue(ingredient_exists)

    def test_create_ingredient_invalid_name(self):
        """Test that ingredient with invalid name is not created"""
        res = self.client.post(INGREDIENT_URL, {"name": ''})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_ingredient_with_assigned_to_recipes(self):
        """Test to filter ingredients that are assigned to recipes"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='one'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='two'
        )
        recipe = Recipe.objects.create(
            user=self.user,
            title='Cake',
            time_minutes=13,
            price=7.05
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_ingredient_with_assigned_recipe_unique(self):
        """Test filter ingredients with those assigned to recipe are unique"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='one'
        )
        Ingredient.objects.create(
            user=self.user,
            name='two'
        )

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Cake',
            time_minutes=13,
            price=7.05
        )
        recipe1.ingredients.add(ingredient)

        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Cake',
            time_minutes=13,
            price=7.05
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)

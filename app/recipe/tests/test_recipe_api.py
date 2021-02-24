from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """create and return detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='meat'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='paper'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        """Test viewing of recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        serializer = RecipeDetailSerializer(recipe)

        url = detail_url(recipe.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test that basic recipe is created successfully"""
        payload = {
            'title': "chocolate cake",
            'time_minutes': 30,
            'price': 7.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipes_with_tags(self):
        """Test creating recipe with tags"""
        tag1 = sample_tag(self.user, name='vegan')
        tag2 = sample_tag(self.user, name='barbra')

        payload = {
            'title': 'Lala',
            'time_minutes': 7,
            'price': 23.50,
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredient(self):
        """Test create recipe with ingredient"""
        ingredient1 = sample_ingredient(self.user, 'paper')
        ingredient2 = sample_ingredient(self.user, 'salt')

        payload = {
            'title': 'Maya',
            'time_minutes': 7,
            'price': 23.50,
            'ingredients': [ingredient1.id, ingredient2.id]
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating recipe with patch method"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Asman')
        payload = {
            'title': 'Chicken soup',
            'tags': [new_tag.id]
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating recipe with put method"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spageti with meat',
            'time_minutes': 30,
            'price': 100.00,
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)
        recipe.refresh_from_db()

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

        self.assertEqual(len(recipe.tags.all()), 0)

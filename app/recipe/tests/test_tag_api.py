from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import TagSerializer
from core.models import Tag, Recipe

TAGS_URL = reverse('recipe:tag-list')


class PublicTagAPITest(TestCase):
    """Test public api tags"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITest(TestCase):
    """Tests that requires authentication"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(email='salman@gmail.com',
                                                    password='test1234')
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test for retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        Tag.objects.create(user=self.user, name='Launch')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limit_tag_to_user(self):
        """Test that logged in user gets his/her own recipes"""
        user2 = get_user_model().objects.create_user(
            email='another@gmail.com', password='test1234')
        Tag.objects.create(user=user2, name='Bread')
        tag = Tag.objects.create(user=self.user, name='Diary')
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_creat_tag_successful(self):
        """Test for creating tag"""
        payload = {"name": "created tag"}
        self.client.post(TAGS_URL, payload)
        tag_exists = Tag.objects.filter(
            user=self.user, name=payload.get('name')
        ).exists()
        self.assertTrue(tag_exists)

    def test_invalid_tag_name(self):
        """Test that invalid names raise validation error"""
        res = self.client.post(TAGS_URL, {"name": '', })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='one')
        tag2 = Tag.objects.create(user=self.user, name='two')
        recipe = Recipe.objects.create(user=self.user,
                                       title='Stake barbra',
                                       time_minutes=39,
                                       price=15.00)
        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL,
                              {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_to_recipes_unique(self):
        """Filtering tags by those assigned to recipes are unique"""
        tag1 = Tag.objects.create(user=self.user, name='one')
        Tag.objects.create(user=self.user, name='two')

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Stake barbra',
            time_minutes=39,
            price=15.00)
        recipe1.tags.add(tag1)

        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Stake barbra',
            time_minutes=39,
            price=15.00)
        recipe2.tags.add(tag1)

        res = self.client.get(TAGS_URL,
                              {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

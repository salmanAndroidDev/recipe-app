from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import TagSerializer
from core.models import Tag

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

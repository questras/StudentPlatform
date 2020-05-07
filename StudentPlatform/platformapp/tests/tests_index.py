from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


def create_test_user(name, password):
    """Create test user for testing purposes."""

    user = User.objects.create_user(username=name, password=password)
    user.save()

    return user


class IndexViewTests(TestCase):
    """Tests for index_view"""

    def authenticate(self, name, password):
        """Create test user and authenticate for testing purposes."""
        self.user = User.objects.create_user(username=name, password=password)

    def test_not_logged_user_can_access_index_view(self):
        """Test if not logged user can access index_view"""
        response = self.client.get(reverse('index_view'))

        self.assertEqual(response.status_code, 200)

    def test_logged_user_is_redirected_to_feed(self):
        """Test if logged user is redirected to feed_view"""
        self.authenticate('test', 'test')

        is_logged = self.client.login(username='test', password='test')
        self.assertTrue(is_logged)

        response = self.client.get(reverse('index_view'))
        self.assertRedirects(response, expected_url=reverse('feed_view'))

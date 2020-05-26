from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from . import utils_for_testing as utils

User = get_user_model()


class IndexViewTests(TestCase):
    """Tests for index_view"""

    def setUp(self) -> None:
        self.url = reverse('index_view')

    def test_not_logged_user_can_access_index_view(self):
        """Test if not logged user can access index_view"""

        utils.test_can_access(self, self.url)

    def test_logged_user_is_redirected_to_feed(self):
        """Test if logged user is redirected to feed_view"""

        utils.create_user_and_authenticate(self)

        response = self.client.get(self.url)
        self.assertRedirects(response, expected_url=reverse('feed_view'))


class HowToViewTests(TestCase):
    """Tests for how_to_view."""

    def setUp(self) -> None:
        self.url = reverse('how_to_view')

    def test_not_logged_user_can_access(self):
        """Test if not logged user can access."""

        utils.test_can_access(self, self.url)

    def test_logged_user_can_access(self):
        """Test if logged user can access."""

        utils.create_user_and_authenticate(self)
        utils.test_can_access(self, self.url)

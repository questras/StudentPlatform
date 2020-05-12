from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from . import utils_for_testing as utils

User = get_user_model()


class IndexViewTests(TestCase):
    """Tests for index_view"""

    def test_not_logged_user_can_access_index_view(self):
        """Test if not logged user can access index_view"""

        response = self.client.get(reverse('index_view'))
        self.assertEqual(response.status_code, 200)

    def test_logged_user_is_redirected_to_feed(self):
        """Test if logged user is redirected to feed_view"""

        utils.create_user_and_authenticate(self)

        response = self.client.get(reverse('index_view'))
        self.assertRedirects(response, expected_url=reverse('feed_view'))

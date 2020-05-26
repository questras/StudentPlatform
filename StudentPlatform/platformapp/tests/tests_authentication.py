from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

from . import utils_for_testing as utils

User = get_user_model()


class SignUpViewTests(TestCase):
    """Tests for SignUpView."""

    def setUp(self) -> None:
        self.url = reverse('signup_view')
        self.data = {
            'username': 'test',
            'password1': 'testtesttest',
            'password2': 'testtesttest',
        }

    def test_logged_in_cannot_sign_up(self):
        """Test if logged in user cannot sign up"""

        utils.create_user_and_authenticate(self)

        # Get request redirects to feed_view.
        response = self.client.get(self.url)
        self.assertRedirects(response, expected_url=reverse('feed_view'))

        # Post request redirects to feed_view.
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, expected_url=reverse('feed_view'))

    def test_not_logged_in_can_sign_up(self):
        """Test if not logged in user can sign up."""

        utils.test_can_access(self, self.url,
                              post_redirect_url=reverse('login_view'),
                              data=self.data)
        self.assertEquals(len(User.objects.all()), 1)

    def test_cannot_sign_up_with_existing_username(self):
        """Test if cannot sign up with existing username or email"""

        User.objects.create_user(
            username='test',
            password='test',
        ).save()

        response = self.client.post(reverse('signup_view'), self.data)
        # No redirect code.
        self.assertEquals(response.status_code, 200)
        # Exists only one user created earlier.
        self.assertEquals(len(User.objects.all()), 1)


class LogoutViewTests(TestCase):
    """Tests for logout_view"""

    def test_logged_user_can_logout(self):
        """Test if logged user can logout."""

        utils.create_user_and_authenticate(self)

        response = self.client.get(reverse('logout_view'))
        self.assertRedirects(response, reverse('index_view'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_not_logged_user_redirected(self):
        """Test if not logged user is redirected."""

        response = self.client.get(reverse('logout_view'))
        self.assertRedirects(response, reverse('index_view'))
        self.assertNotIn('_auth_user_id', self.client.session)

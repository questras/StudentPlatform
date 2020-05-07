from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpViewTests(TestCase):
    """Tests for SignUpView."""

    def create_user(self, name, password):
        """Create test user for testing purposes."""

        self.user = User.objects.create_user(username=name, password=password)

    def test_logged_in_cannot_sign_up(self):
        """Test if logged in user cannot sign up"""

        self.create_user('test', 'test')
        is_logged = self.client.login(username='test', password='test')
        self.assertTrue(is_logged)

        # Get request redirects to feed_view.
        response = self.client.get(reverse('signup_view'))
        self.assertRedirects(response, expected_url=reverse('feed_view'))

        # Post request redirects to feed_view.
        signup_data = {
            'username': 'test',
            'password1': 'testtesttest',
            'password2': 'testtesttest',
        }
        response = self.client.post(reverse('signup_view'), signup_data)
        self.assertRedirects(response, expected_url=reverse('feed_view'))

    def test_not_logged_in_can_sign_up(self):
        """Test if not logged in user can sign up."""

        response = self.client.get(reverse('signup_view'))
        self.assertEquals(response.status_code, 200)

        signup_data = {
            'username': 'test',
            'password1': 'testtesttest',
            'password2': 'testtesttest',
        }
        response = self.client.post(reverse('signup_view'), signup_data)
        self.assertRedirects(response, expected_url=reverse('login_view'))
        self.assertEquals(len(User.objects.all()), 1)

    def test_cannot_sign_up_with_existing_username(self):
        """Test if cannot sign up with existing username or email"""

        User.objects.create_user(
            username='test',
            password='test',
            email='test@test.com'
        ).save()

        signup_data = {
            'username': 'test',
            'password1': 'testtesttest',
            'password2': 'testtesttest',
        }

        response = self.client.post(reverse('signup_view'), signup_data)
        # No redirect code.
        self.assertEquals(response.status_code, 200)
        # Exists only one user created earlier.
        self.assertEquals(len(User.objects.all()), 1)

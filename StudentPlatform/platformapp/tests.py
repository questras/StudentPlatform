from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


def login_user(self, superuser=False):
    """Create user or superuser and log in for testing purposes"""
    if superuser:
        self.user = User.objects.create_superuser(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
    else:
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')


class IndexViewTests(TestCase):
    """Tests related to Index view"""

    def test_logged_in(self):
        """
        Test: logged in user can access Index view and sees his username
        in the top right corner
         """
        login_user(self)
        response = self.client.get(reverse('index'))

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_not_logged_in(self):
        """
        Test: not logged user can access Index view and sees
        'You need to be logged in' information
         """
        response = self.client.get(reverse('index'))

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'You need to be logged in')


class SignUpViewTests(TestCase):
    """Tests related to SignUp view"""

    def test_logged_in_cannot_sign_up(self):
        """Test: logged in user cannot sign up"""
        login_user(self)
        response = self.client.get(reverse('signup'))

        self.assertEquals(response.status_code, 302)

    def test_not_logged_in_can_sign_up(self):
        """
        Test: not logged in user can sign up
        """
        response = self.client.get(reverse('signup'))
        self.assertEquals(response.status_code, 200)

        response = self.client.post(
            reverse('signup'),
            {
                'username': 'testuser',
                'first_name': 'testuser',
                'last_name': 'testuser',
                'email': 'testuser@testuser.com',
                'password1': 'iamtesting123',
                'password2': 'iamtesting123',
            }
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(User.objects.all()), 1)

    def test_cannot_sign_up_existing_username_or_email(self):
        """Test: user cannot sign up with existing username or email"""
        User.objects.create_user(
            username='testuser',
            password='12345',
            email='testuser@testuser.com'
        ).save()

        response = self.client.get(reverse('signup'))
        self.assertEquals(response.status_code, 200)

        response = self.client.post(
            reverse('signup'),
            {
                'username': 'testuser',
                'first_name': 'testuser',
                'last_name': 'testuser',
                'email': 'notthesame@testuser.com',
                'password1': 'iamtesting123',
                'password2': 'iamtesting123',
            }
        )
        self.assertEquals(response.status_code, 200)  # no redirect code
        self.assertEquals(len(User.objects.all()), 1)  # exists only one user created earlier

        response = self.client.post(
            reverse('signup'),
            {
                'username': 'notthesame',
                'first_name': 'testuser',
                'last_name': 'testuser',
                'email': 'testuser@testuser.com',
                'password1': 'iamtesting123',
                'password2': 'iamtesting123',
            }
        )
        self.assertEquals(response.status_code, 200)  # no redirect code
        self.assertEquals(len(User.objects.all()), 1)  # exists only one user created earlier


class LoginViewTests(TestCase):
    def test_logged_in_user_cannot_login(self):
        """Test: logged in user cannot access Login view"""
        login_user(self)

        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 302)    # redirect code

    def test_not_logged_in_user_can_login(self):
        """Test: not logged in user can access Login view and log in"""
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)

        User.objects.create_user(username='testuser', password='12345').save()
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})

        self.assertEquals(response.status_code, 302)    # redirect code



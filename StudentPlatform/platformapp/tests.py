from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Group
from django.contrib.auth import get_user_model

User = get_user_model()


def login_user(self, superuser=False):
    """Create user or superuser and log in for testing purposes"""
    if superuser:
        self.user = User.objects.create_superuser(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
    else:
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')


def redirect_next(url1, url2):
    """Return redirect url with 'next' attribute"""
    return '{}?next={}'.format(reverse(url1), reverse(url2))


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

        self.assertRedirects(response, expected_url=reverse('index'))

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
        self.assertRedirects(response, expected_url=reverse('login'))
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
        self.assertRedirects(response, expected_url=reverse('index'))

    def test_not_logged_in_user_can_login(self):
        """Test: not logged in user can access Login view and log in"""
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)

        User.objects.create_user(username='testuser', password='12345').save()
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})

        self.assertRedirects(response, expected_url=reverse('index'))


class CreateGroupTests(TestCase):
    """Tests related to Create Group view"""

    def test_not_logged_in_cannot_access(self):
        """Test: not logged in user cannot access Create Group view"""
        response = self.client.get(reverse('create_group'))
        self.assertRedirects(response, expected_url=redirect_next('login', 'create_group'))

    def test_cannot_create_group_with_empty_field(self):
        """Test: cannot create group with one or more empty fields"""
        login_user(self)
        response = self.client.get(reverse('create_group'))
        self.assertEquals(response.status_code, 200)

        response = self.client.post(reverse('create_group'), {'name': 'group_name'})
        self.assertNotEquals(response.status_code, 302)  # no redirect code

        response = self.client.post(reverse('create_group'), {'description': 'group_desc'})
        self.assertNotEquals(response.status_code, 302)  # no redirect code

    def test_user_can_create_group(self):
        """Test: user can create group"""
        login_user(self)
        response = self.client.get(reverse('create_group'))
        self.assertEquals(response.status_code, 200)

        response = self.client.post(reverse('create_group'), {'name': 'n', 'description': 'd'})
        self.assertRedirects(response,
                             expected_url=reverse('index'))  # for now placeholder: index, "groups" in the future

        created_group = Group.objects.all()
        self.assertEquals(len(created_group), 1)  # contains one group just created

        self.assertEquals(created_group[0].name, 'n')
        self.assertEquals(created_group[0].description, 'd')
        self.assertEquals(created_group[0].creator, self.user)
        self.assertEquals(created_group[0].share_url, 'placeholder.com')

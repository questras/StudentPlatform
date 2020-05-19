from django.contrib.auth import get_user_model
from django.test import TestCase
from django.shortcuts import reverse

User = get_user_model()
LOGIN_URL = reverse('login_view')


def create_user(name, password):
    """Create user for testing purposes."""

    user = User.objects.create_user(username=name, password=password)
    return user


def create_user_and_authenticate(test_case: TestCase):
    """Create user for testing purposes, save him as
    test_case's variable [user] and log in."""

    test_case.logged_user = create_user('logged', 'logged')
    test_case.client.login(username='logged', password='logged')


def create_two_users_authenticate_one(test_case: TestCase):
    """Create two users for testing purposes, save them
    as test_case's variables [logged_user] and [not_logged_user]
    and authenticate [logged_user]."""

    test_case.logged_user = create_user('logged', 'logged')
    test_case.not_logged_user = create_user('notlogged', 'notlogged')
    test_case.client.login(username='logged', password='logged')


def login_redirect_url(url):
    """Return url to login view with next query set to [url]."""
    return f'{LOGIN_URL}?next={url}'


def test_not_logged_cannot_access(test_case: TestCase, url: str,
                                  data: dict = None):
    """Cannot access test with login redirect url as expected url."""

    expected_url = login_redirect_url(url)
    test_cannot_access(test_case, url, expected_url, data)


def test_cannot_access(test_case: TestCase, url: str,
                       expected_url: str, data: dict = None):
    """Check if test_case cannot access url with
    GET request and POST request with optional data and
    is redirected to expected_url."""

    response = test_case.client.get(url)
    test_case.assertRedirects(response, expected_url=expected_url)

    response = test_case.client.post(url, data)
    test_case.assertRedirects(response, expected_url=expected_url)


def test_can_access(test_case: TestCase,
                    url: str,
                    get_expected_url: str = None,
                    post_expected_url: str = None,
                    data: dict = None):
    """Check if test_case can access url with
    GET request and POST request with optional data and
    is redirected to expected url, if specified."""

    response = test_case.client.get(url)
    if get_expected_url:
        test_case.assertRedirects(response, expected_url=get_expected_url)
    else:
        test_case.assertEqual(response.status_code, 200)

    response = test_case.client.post(url, data)
    if post_expected_url:
        test_case.assertRedirects(response, expected_url=post_expected_url)
    else:
        test_case.assertEqual(response.status_code, 200)
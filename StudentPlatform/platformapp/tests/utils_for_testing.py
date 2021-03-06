from django.contrib.auth import get_user_model
from django.test import TestCase
from django.shortcuts import reverse
from typing import List, Tuple

User = get_user_model()
LOGIN_URL = reverse('login_view')


def create_user(name: str, password: str) -> User:
    """Create user for testing purposes."""

    user = User.objects.create_user(username=name, password=password)
    return user


def create_user_and_authenticate(test_case: TestCase) -> User:
    """Create user for testing purposes, log in and return
    authenticated user."""

    logged_user = create_user('logged', 'logged')
    test_case.client.login(username='logged', password='logged')

    return logged_user


def create_two_users_authenticate_one(test_case: TestCase) \
        -> Tuple[User]:
    """Create two users for testing purposes, authenticate
    one and return them."""

    logged_user = create_user('logged', 'logged')
    not_logged_user = create_user('notlogged', 'notlogged')
    test_case.client.login(username='logged', password='logged')

    return logged_user, not_logged_user


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
                    get_redirect_url: str = None,
                    post_redirect_url: str = None,
                    data: dict = None):
    """Check if test_case can access url with
    GET request and POST request with optional data and
    is redirected to expected url, if specified."""

    response = test_case.client.get(url)
    if get_redirect_url:
        test_case.assertRedirects(response, expected_url=get_redirect_url)
    else:
        test_case.assertEqual(response.status_code, 200)

    response = test_case.client.post(url, data)
    if post_redirect_url:
        test_case.assertRedirects(response, expected_url=post_redirect_url)
    else:
        test_case.assertEqual(response.status_code, 200)


def test_cannot_post_with_empty_fields(test_case: TestCase,
                                       url: str,
                                       fields: List[str]):
    """Check if POST requests to url with missing data fields
    return 400 response code."""

    # Check post request with no data.
    response = test_case.client.post(url, data={})
    test_case.assertEqual(response.status_code, 400)

    # Check post request with only one field filled.
    if len(fields) > 1:
        for field in fields:
            response = test_case.client.post(url, data={field: 'test'})
            test_case.assertEqual(response.status_code, 400)

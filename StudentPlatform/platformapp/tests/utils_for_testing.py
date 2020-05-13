from django.contrib.auth import get_user_model
from django.test import TestCase
from django.shortcuts import reverse

from ..models import Group, Tab, Element

User = get_user_model()


def create_user(name, password):
    """Create user for testing purposes."""

    user = User.objects.create_user(username=name, password=password)
    return user


def create_user_and_authenticate(test_case: TestCase):
    """Create user for testing purposes, save him as
    test_case's variable [user] and log in."""

    test_case.user = create_user('test', 'test')
    test_case.client.login(username='test', password='test')


def create_two_users_authenticate_one(test_case: TestCase):
    """Create two users for testing purposes, save them
    as test_case's variables [logged_user] and [not_logged_user]
    and authenticate [logged_user]."""

    test_case.logged_user = create_user('logged', 'logged')
    test_case.not_logged_user = create_user('not_logged', 'not_logged')
    test_case.client.login(username='logged', password='logged')


def create_group(name, description, user):
    """Create group for testing purposes"""

    group = Group.objects.create(
        name=name,
        description=description,
        creator=user,
    )
    group.save()
    group.users.add(user)
    group.save()

    return group


def create_tab(name, user, group):
    """Create Tab for testing purposes"""

    tab = Tab.objects.create(
        name=name,
        creator=user,
        group=group,
    )
    tab.save()

    return tab


def create_element(name, text, user, tab):
    """Create element for testing purposes"""

    element = Element.objects.create(
        name=name,
        text=text,
        creator=user,
        tab=tab,
    )
    element.save()

    return element


def login_redirect_url(url):
    """Return url to login view with next query set to [url]."""
    login_url = reverse('login_view')
    return f'{login_url}?next={url}'

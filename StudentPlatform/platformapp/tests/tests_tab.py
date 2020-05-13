from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from ..models import Tab
from . import utils_for_testing as utils

User = get_user_model()


class CreateTabViewTests(TestCase):
    """Tests for create_tab_view."""

    def test_not_logged_cannot_create_tab(self):
        """Test if not logged user cannot create a tab."""

        not_logged_user = utils.create_user('test', 'test')
        group = utils.create_group('test', 'test', not_logged_user)

        tab_url = reverse('create_tab_view', args=(group.pk,))
        expected_url = utils.login_redirect_url(tab_url)

        response = self.client.get(tab_url)
        self.assertRedirects(response, expected_url=expected_url)

        data = {
            'name': 'name',
        }
        response = self.client.post(tab_url, data)
        self.assertRedirects(response, expected_url=expected_url)
        self.assertEqual(len(Tab.objects.all()), 0)

    def test_user_not_in_group_cannot_create(self):
        """Test if user not in group cannot create a tab."""

        utils.create_two_users_authenticate_one(self)
        group = utils.create_group('test', 'test', self.not_logged_user)

        tab_url = reverse('create_tab_view', args=(group.pk,))
        expected_url = reverse('my_groups_view')

        response = self.client.get(tab_url)
        self.assertRedirects(response, expected_url=expected_url)

        data = {
            'name': 'name',
        }
        response = self.client.post(tab_url, data)
        self.assertRedirects(response, expected_url=expected_url)
        self.assertEqual(len(Tab.objects.all()), 0)

    def test_user_in_group_can_create_tab(self):
        """Test if user in group can create tab."""

        utils.create_user_and_authenticate(self)
        group = utils.create_group('test', 'test', self.logged_user)
        tab_url = reverse('create_tab_view', args=(group.pk,))
        expected_url = reverse('group_view', args=(group.pk,))

        response = self.client.get(tab_url)
        self.assertEqual(response.status_code, 200)

        data = {
            'name': 'name',
        }
        response = self.client.post(tab_url, data)
        self.assertRedirects(response, expected_url=expected_url)
        self.assertEqual(len(Tab.objects.all()), 1)

    def test_cannot_create_tab_with_empty_field(self):
        """Test if cannot create tab with empty field."""

        utils.create_user_and_authenticate(self)
        group = utils.create_group('test', 'test', self.logged_user)
        tab_url = reverse('create_tab_view', args=(group.pk,))

        data = {}
        response = self.client.post(tab_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(Tab.objects.all()), 0)

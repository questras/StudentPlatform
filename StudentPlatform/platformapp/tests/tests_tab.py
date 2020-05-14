from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from ..models import Tab
from . import utils_for_testing as utils

User = get_user_model()


class CreateTabViewTests(TestCase):
    """Tests for create_tab_view."""

    def setUp(self) -> None:
        self.not_logged_user = utils.create_user('notlogged', 'notlogged')
        self.group = utils.create_group('test', 'test', self.not_logged_user)
        self.url = reverse('create_tab_view', args=(self.group.pk,))
        self.data = {
            'name': 'new',
        }

    def test_not_logged_cannot_create_tab(self):
        """Test if not logged user cannot create a tab."""

        utils.test_not_logged_cannot_access(self, self.url, self.data)

    def test_user_not_in_group_cannot_create_tab(self):
        """Test if user not in group cannot create a tab."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        response = self.client.get(self.url)
        self.assertRedirects(response, expected_url=expected_url)

        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, expected_url=expected_url)
        self.assertEqual(len(Tab.objects.all()), 0)

    def test_user_in_group_can_create_tab(self):
        """Test if user in group can create tab."""

        utils.create_user_and_authenticate(self)
        self.group.users.add(self.logged_user)
        expected_url = reverse('group_view', args=(self.group.pk,))

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, expected_url=expected_url)
        self.assertEqual(len(Tab.objects.all()), 1)

    def test_cannot_create_tab_with_empty_field(self):
        """Test if cannot create tab with empty field."""

        utils.create_user_and_authenticate(self)
        self.group.users.add(self.logged_user)

        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(Tab.objects.all()), 0)

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from ..models import Group

User = get_user_model()


class CreateGroupViewTests(TestCase):
    """Tests for CreateGroupView."""

    def create_user_and_authenticate(self, name, password):
        """Create test user and authenticate for testing purposes."""

        self.user = User.objects.create_user(username=name, password=password)
        self.client.login(username=name, password=password)

    def test_not_logged_cannot_create_group(self):
        """Test if not logged user cannot create group."""

        login_url = reverse('login_view')
        create_url = reverse('create_group_view')
        response = self.client.get(create_url)
        self.assertRedirects(response, f'{login_url}?next={create_url}')

        data = {
            'name': 'name',
            'description': 'description',
        }
        response = self.client.post(create_url, data)
        self.assertRedirects(response, f'{login_url}?next={create_url}')

    def test_logged_can_create_group(self):
        """Test if logged user can create group."""

        self.create_user_and_authenticate('test', 'test')

        response = self.client.get(reverse('create_group_view'))
        self.assertEqual(response.status_code, 200)

        data = {
            'name': 'name',
            'description': 'description',
        }
        response = self.client.post(reverse('create_group_view'), data)
        self.assertRedirects(response, reverse('my_groups_view'))
        groups = Group.objects.all()
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, 'name')
        self.assertEqual(groups[0].description, 'description')
        self.assertEqual(groups[0].creator, self.user)
        self.assertEqual(len(groups[0].users.all()), 1)

    def test_cannot_create_group_with_empty_field(self):
        """Test if cannot create group with one or more empty fields"""

        self.create_user_and_authenticate('test', 'test')

        data = {'name': 'name'}
        response = self.client.post(reverse('create_group_view'), data)
        self.assertEqual(response.status_code, 400)

        data = {'description': 'description'}
        response = self.client.post(reverse('create_group_view'), data)
        self.assertEqual(response.status_code, 400)

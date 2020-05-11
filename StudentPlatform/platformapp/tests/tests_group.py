from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from ..models import Group

User = get_user_model()


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


class JoinGroupViewTests(TestCase):
    """Tests for join_group_view"""

    def create_user_and_authenticate(self, name, password):
        """Create test user and authenticate for testing purposes."""

        self.user = User.objects.create_user(username=name, password=password)
        self.client.login(username=name, password=password)

    def test_not_logged_user_cannot_access(self):
        """Test if not logged user cannot join group."""

        some_user = User.objects.create_user(username='test', password='test')
        group = create_group('test', 'test', some_user)

        join_url = reverse('join_group_view', args=(group.pk,))
        login_url = reverse('login_view')

        response = self.client.get(join_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={join_url}')

        response = self.client.post(join_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={join_url}')

    def test_logged_user_can_join(self):
        """Test if logged user can join group."""

        self.create_user_and_authenticate('test', 'test')
        some_user = User.objects.create_user(username='some', password='some')
        group = create_group('test', 'test', some_user)
        join_url = reverse('join_group_view', args=(group.pk,))

        response = self.client.get(join_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(join_url)
        self.assertRedirects(response, reverse('my_groups_view'))
        self.assertIn(self.user, group.users.all())
        self.assertIn(group, self.user.joined_groups.all())

    def test_logged_user_already_joined_is_redirected(self):
        """Test if logged user who already joined
        the group is redirected."""

        self.create_user_and_authenticate('test', 'test')
        group = create_group('test', 'test', self.user)
        join_url = reverse('join_group_view', args=(group.pk,))

        response = self.client.get(join_url)
        self.assertRedirects(response, reverse('my_groups_view'))

        response = self.client.post(join_url)
        self.assertRedirects(response, reverse('my_groups_view'))


class MyGroupsViewTests(TestCase):
    """Tests for my_groups_view."""

    def create_user_and_authenticate(self, name, password):
        """Create test user and authenticate for testing purposes."""

        self.user = User.objects.create_user(username=name, password=password)
        self.client.login(username=name, password=password)

    def test_not_logged_user_cannot_access(self):
        """Test if not logged user cannot access the view."""

        some_user = User.objects.create_user(username='test', password='test')
        group = create_group('test', 'test', some_user)

        groups_url = reverse('my_groups_view')
        login_url = reverse('login_view')
        response = self.client.get(groups_url)
        self.assertRedirects(response, f'{login_url}?next={groups_url}')

    def test_logged_user_can_access(self):
        """Test if logged user can access the view."""

        self.create_user_and_authenticate('test', 'test')

        response = self.client.get(reverse('my_groups_view'))
        self.assertEqual(response.status_code, 200)

    def test_logged_user_see_only_joined_groups(self):
        """Test if logged user see only joined groups."""

        self.create_user_and_authenticate('test', 'test')
        seen_group = create_group('seen', 'seen', self.user)
        some_user = User.objects.create_user(username='some', password='some')
        not_seen_group = create_group('not_seen', 'not_seen', some_user)

        response = self.client.get(reverse('my_groups_view'))
        seen_groups = response.context['groups']
        self.assertEqual(len(seen_groups), 1)
        self.assertIn(seen_group, seen_groups)
        self.assertNotIn(not_seen_group, seen_groups)


class LeaveGroupViewTests(TestCase):
    """Tests for leave_group_view"""

    def create_user_and_authenticate(self, name, password):
        """Create test user and authenticate for testing purposes."""

        self.user = User.objects.create_user(username=name, password=password)
        self.client.login(username=name, password=password)

    def test_not_logged_user_cannot_leave(self):
        """Test if not logged user cannot leave any group."""

        some_user = User.objects.create_user(username='test', password='test')
        group = create_group('test', 'test', some_user)

        leave_url = reverse('leave_group_view', args=(group.pk,))
        login_url = reverse('login_view')

        response = self.client.get(leave_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={leave_url}')

        response = self.client.post(leave_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={leave_url}')

    def test_logged_user_in_group_can_leave(self):
        """Test if logged user in group can leave it."""

        self.create_user_and_authenticate('test', 'test')
        group = create_group('test', 'test', self.user)
        leave_url = reverse('leave_group_view', args=(group.pk,))

        response = self.client.get(leave_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(leave_url)
        self.assertRedirects(response, reverse('my_groups_view'))
        self.assertNotIn(self.user, group.users.all())
        self.assertNotIn(group, self.user.joined_groups.all())

    def test_logged_user_not_in_group_is_redirected(self):
        """Test if logged user not in group is redirected."""

        self.create_user_and_authenticate('test', 'test')
        some_user = User.objects.create_user(username='some', password='some')
        group = create_group('test', 'test', some_user)
        leave_url = reverse('leave_group_view', args=(group.pk,))

        response = self.client.get(leave_url)
        self.assertRedirects(response, reverse('my_groups_view'))

        response = self.client.post(leave_url)
        self.assertRedirects(response, reverse('my_groups_view'))
        self.assertNotIn(self.user, group.users.all())
        self.assertNotIn(group, self.user.joined_groups.all())

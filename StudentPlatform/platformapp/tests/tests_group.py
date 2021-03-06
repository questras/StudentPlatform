from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from ..models import Group
from .. import scripts
from . import utils_for_testing as utils

User = get_user_model()


class CreateGroupViewTests(TestCase):
    """Tests for CreateGroupView."""

    def setUp(self) -> None:
        self.url = reverse('create_group_view')
        self.data = {
            'name': 'name',
            'description': 'description',
        }

    def test_not_logged_cannot_create_group(self):
        """Test if not logged user cannot create group."""

        utils.test_not_logged_cannot_access(self, self.url, self.data)

    def test_logged_can_create_group(self):
        """Test if logged user can create group."""

        logged_user = utils.create_user_and_authenticate(self)
        utils.test_can_access(self, self.url,
                              post_redirect_url=reverse('my_groups_view'),
                              data=self.data)

        groups = Group.objects.all()
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, self.data['name'])
        self.assertEqual(groups[0].description, self.data['description'])
        self.assertEqual(groups[0].creator, logged_user)
        self.assertEqual(len(groups[0].users.all()), 1)

    def test_cannot_create_group_with_empty_field(self):
        """Test if cannot create group with one or more empty fields"""

        utils.create_user_and_authenticate(self)
        group_fields = ['name', 'description']
        utils.test_cannot_post_with_empty_fields(self, self.url, group_fields)


class UpdateGroupViewTests(TestCase):
    """Tests for update_group_view."""

    def setUp(self) -> None:
        self.not_logged_user = utils.create_user('notlogged', 'notlogged')
        self.group = scripts.create_group('test', 'test', self.not_logged_user)
        self.url = reverse('update_group_view', args=(self.group.pk,))
        self.data = {
            'name': 'new',
            'description': 'new',
        }

    def test_not_logged_cannot_update(self):
        """Test if not logged user cannot update a group."""

        utils.test_not_logged_cannot_access(self, self.url, self.data)

    def test_user_not_in_group_cannot_update(self):
        """Test if user who is not in the group cannot update and is
        redirected to my_groups_view."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.url,
                                 expected_url=expected_url,
                                 data=self.data)

    def test_not_creator_cannot_update(self):
        """Test if user who is not a creator of group cannot update
        and is redirected to my_groups_view."""

        logged_user = utils.create_user_and_authenticate(self)
        self.group.users.add(logged_user)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.url,
                                 expected_url=expected_url,
                                 data=self.data)

    def test_creator_in_group_can_update(self):
        """Test if creator of group who is in it can update."""

        self.client.login(username='notlogged', password='notlogged')
        expected_url = reverse('group_view', args=(self.group.pk,))

        utils.test_can_access(self, self.url,
                              post_redirect_url=expected_url,
                              data=self.data)

        updated_group = Group.objects.get(pk=self.group.pk)
        self.assertEqual(updated_group.name, self.data['name'])
        self.assertEqual(updated_group.description, self.data['description'])
        self.assertIsNotNone(updated_group.last_edit_date)

    def test_cannot_update_with_empty_field(self):
        """Test if cannot update group with one or more empty fields"""

        self.client.login(username='notlogged', password='notlogged')
        group_fields = ['name', 'description']

        utils.test_cannot_post_with_empty_fields(self, self.url, group_fields)

        # Group is not updated.
        updated_group = Group.objects.get(pk=self.group.pk)
        self.assertEqual(updated_group.name, 'test')
        self.assertEqual(updated_group.description, 'test')
        self.assertIsNone(updated_group.last_edit_date)


class DeleteGroupViewTests(TestCase):
    """Tests for DeleteGroupView."""

    def setUp(self) -> None:
        self.not_logged_user = utils.create_user('notlogged', 'notlogged')
        self.group = scripts.create_group('test', 'test', self.not_logged_user)
        self.url = reverse('delete_group_view', args=(self.group.pk,))

    def test_not_logged_cannot_delete(self):
        """Test if not logged user cannot delete a group."""

        utils.test_not_logged_cannot_access(self, self.url)

    def test_user_not_in_group_cannot_delete(self):
        """Test if user who is not in the group cannot delete and is
        redirected to my_groups_view."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.url, expected_url)
        self.assertEqual(len(Group.objects.all()), 1)

    def test_not_creator_cannot_delete(self):
        """Test if user who is not a creator of group cannot delete
        and is redirected to my_groups_view."""

        logged_user = utils.create_user_and_authenticate(self)
        self.group.users.add(logged_user)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.url, expected_url)
        self.assertEqual(len(Group.objects.all()), 1)

    def test_creator_in_group_can_delete(self):
        """Test if creator of group who is in it can delete."""

        self.client.login(username='notlogged', password='notlogged')
        expected_url = reverse('my_groups_view')

        utils.test_can_access(self, self.url,
                              post_redirect_url=expected_url)
        self.assertEqual(len(Group.objects.all()), 0)


class GroupViewTests(TestCase):
    """Tests for group_view."""

    def setUp(self) -> None:
        self.not_logged_user = utils.create_user('notlogged', 'notlogged')
        self.group = scripts.create_group('test', 'test', self.not_logged_user)
        self.url = reverse('group_view', args=(self.group.pk,))

    def test_not_logged_user_cannot_access(self):
        """Test if not logged user cannot access the group's view."""

        utils.test_not_logged_cannot_access(self, self.url)

    def test_user_not_in_group_cannot_access(self):
        """Test if user not in the group cannot access
        the group's view."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.url, expected_url)

    def test_user_in_group_can_access(self):
        """Test if user in the group can access the group's view."""

        logged_user = utils.create_user_and_authenticate(self)
        self.group.users.add(logged_user)

        utils.test_can_access(self, self.url)


class GroupMembersViewTests(TestCase):
    """Tests for group_members_view."""

    def setUp(self) -> None:
        self.not_logged_user = utils.create_user('notlogged', 'notlogged')
        self.group = scripts.create_group('test', 'test', self.not_logged_user)
        self.url = reverse('group_members_view', args=(self.group.pk,))

    def test_not_logged_cannot_access(self):
        """Test if not logged user cannot access."""

        utils.test_not_logged_cannot_access(self, self.url)

    def test_logged_user_not_in_group_cannot_access(self):
        """Test if logged user not in group cannot access."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')
        utils.test_cannot_access(self, self.url, expected_url)

    def test_logged_user_in_group_can_access(self):
        """Test if logged user in group can access."""

        logged_user = utils.create_user_and_authenticate(self)
        self.group.users.add(logged_user)

        utils.test_can_access(self, self.url)

    def test_all_users_in_group_are_seen(self):
        """Test if all users in group are in view's context."""

        logged_user = utils.create_user_and_authenticate(self)
        self.group.users.add(logged_user)

        test_users_in_group = []
        test_users_not_in_group = []
        number_of_users = 10

        # Create test users that are in group.
        for i in range(number_of_users):
            user = scripts.create_user(f'test_in{i}', f'test_in{i}')
            test_users_in_group.append(user)
            self.group.users.add(user)

        # Create test users that are not in group.
        for i in range(number_of_users):
            user = scripts.create_user(f'test_not_in{i}', f'test_not_in{i}')
            test_users_not_in_group.append(user)

        response = self.client.get(self.url)
        members = response.context['group'].users.all()

        self.assertIn(logged_user, members)

        for user in test_users_in_group:
            self.assertIn(user, members)

        for user in test_users_not_in_group:
            self.assertNotIn(user, members)


class JoinGroupViewTests(TestCase):
    """Tests for join_group_view"""

    def setUp(self) -> None:
        self.not_logged_user = utils.create_user('notlogged', 'notlogged')
        self.group = scripts.create_group('test', 'test', self.not_logged_user)
        self.url = reverse('join_group_view', args=(self.group.pk,))

    def test_not_logged_user_cannot_access(self):
        """Test if not logged user cannot join group."""

        utils.test_not_logged_cannot_access(self, self.url)

    def test_logged_user_can_join(self):
        """Test if logged user can join group."""

        logged_user = utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        utils.test_can_access(self, self.url,
                              post_redirect_url=expected_url)

        self.assertIn(logged_user, self.group.users.all())
        self.assertIn(self.group, logged_user.joined_groups.all())

    def test_logged_user_already_joined_is_redirected(self):
        """Test if logged user who already joined
        the group is redirected."""

        self.client.login(username='notlogged', password='notlogged')

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('my_groups_view'))

        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('my_groups_view'))


class MyGroupsViewTests(TestCase):
    """Tests for my_groups_view."""

    def setUp(self) -> None:
        self.url = reverse('my_groups_view')

    def test_not_logged_user_cannot_access(self):
        """Test if not logged user cannot access the view."""

        utils.test_not_logged_cannot_access(self, self.url)

    def test_logged_user_can_access(self):
        """Test if logged user can access the view."""

        utils.create_user_and_authenticate(self)
        utils.test_can_access(self, self.url)

    def test_logged_user_see_only_joined_groups(self):
        """Test if logged user see only joined groups."""

        logged_user, not_logged_user = \
            utils.create_two_users_authenticate_one(self)
        seen = scripts.create_group('seen', 'seen', logged_user)
        unseen = scripts.create_group('unseen', 'unseen', not_logged_user)

        response = self.client.get(self.url)
        seen_groups = response.context['groups']

        self.assertEqual(len(seen_groups), 1)
        self.assertIn(seen, seen_groups)
        self.assertNotIn(unseen, seen_groups)


class LeaveGroupViewTests(TestCase):
    """Tests for leave_group_view"""

    def setUp(self) -> None:
        self.not_logged_user = utils.create_user('notlogged', 'notlogged')
        self.group = scripts.create_group('test', 'test', self.not_logged_user)
        self.url = reverse('leave_group_view', args=(self.group.pk,))

    def test_not_logged_user_cannot_leave(self):
        """Test if not logged user cannot leave any group."""

        utils.test_not_logged_cannot_access(self, self.url)

    def test_logged_user_in_group_can_leave(self):
        """Test if logged user in group can leave it."""

        logged_user = utils.create_user_and_authenticate(self)
        self.group.users.add(logged_user)
        expected_url = reverse('my_groups_view')

        utils.test_can_access(self, self.url,
                              post_redirect_url=expected_url)

        self.assertNotIn(logged_user, self.group.users.all())
        self.assertNotIn(self.group, logged_user.joined_groups.all())

    def test_logged_user_not_in_group_is_redirected(self):
        """Test if logged user not in group is redirected."""

        logged_user = utils.create_user_and_authenticate(self)

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('my_groups_view'))

        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('my_groups_view'))
        self.assertNotIn(logged_user, self.group.users.all())
        self.assertNotIn(self.group, logged_user.joined_groups.all())


class SearchGroupsViewTests(TestCase):
    """Test for search_groups_view."""

    def setUp(self) -> None:
        self.url = reverse('search_groups_view')

    def test_not_logged_user_cannot_access(self):
        """Test if not logged user cannot access the view."""

        utils.test_not_logged_cannot_access(self, self.url)

    def test_logged_user_can_access(self):
        """Test if logged user can access the view."""

        utils.create_user_and_authenticate(self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

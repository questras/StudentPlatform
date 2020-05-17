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

        utils.create_user_and_authenticate(self)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, reverse('my_groups_view'))

        groups = Group.objects.all()
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, 'name')
        self.assertEqual(groups[0].description, 'description')
        self.assertEqual(groups[0].creator, self.logged_user)
        self.assertEqual(len(groups[0].users.all()), 1)

    def test_cannot_create_group_with_empty_field(self):
        """Test if cannot create group with one or more empty fields"""

        utils.create_user_and_authenticate(self)

        data = {'name': 'test'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)

        data = {'description': 'test'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)


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

        response = self.client.get(self.url)
        self.assertRedirects(response, expected_url=expected_url)

        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, expected_url=expected_url)

    def test_not_creator_cannot_update(self):
        """Test if user who is not a creator of group cannot update
        and is redirected to my_groups_view."""

        utils.create_user_and_authenticate(self)
        self.group.users.add(self.logged_user)
        expected_url = reverse('my_groups_view')

        response = self.client.get(self.url)
        self.assertRedirects(response, expected_url=expected_url)

        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, expected_url=expected_url)

    def test_creator_in_group_can_update(self):
        """Test if creator of group who is in it can update."""

        self.client.login(username='notlogged', password='notlogged')
        expected_url = reverse('group_view', args=(self.group.pk,))

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, expected_url=expected_url)

        updated_group = Group.objects.get(pk=self.group.pk)
        self.assertEqual(updated_group.name, 'new')
        self.assertEqual(updated_group.description, 'new')

    def test_cannot_update_with_empty_field(self):
        """Test if cannot update group with one or more empty fields"""

        self.client.login(username='notlogged', password='notlogged')
        data_list = [{'name': 'new'}, {'description': 'new'}]

        for data in data_list:
            self.client.post(self.url, data)
            # Group's fields are unchanged.
            group = Group.objects.get(pk=self.group.pk)
            self.assertEqual(group.name, 'test')
            self.assertEqual(group.description, 'test')


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

        response = self.client.get(self.url)
        self.assertRedirects(response, expected_url=expected_url)

        response = self.client.post(self.url)
        self.assertRedirects(response, expected_url=expected_url)
        self.assertEqual(len(Group.objects.all()), 1)

    def test_not_creator_cannot_delete(self):
        """Test if user who is not a creator of group cannot delete
        and is redirected to my_groups_view."""

        utils.create_user_and_authenticate(self)
        self.group.users.add(self.logged_user)
        expected_url = reverse('my_groups_view')

        response = self.client.get(self.url)
        self.assertRedirects(response, expected_url=expected_url)

        response = self.client.post(self.url)
        self.assertRedirects(response, expected_url=expected_url)
        self.assertEqual(len(Group.objects.all()), 1)

    def test_creator_in_group_can_delete(self):
        """Test if creator of group who is in it can delete."""

        self.client.login(username='notlogged', password='notlogged')
        expected_url = reverse('my_groups_view')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url)
        self.assertRedirects(response, expected_url=expected_url)
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

        response = self.client.get(self.url)
        self.assertRedirects(response, expected_url=expected_url)

    def test_user_in_group_can_access(self):
        """Test if user in the group can access the group's view."""

        utils.create_user_and_authenticate(self)
        self.group.users.add(self.logged_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_contains_all_tabs_and_elements_related_to_group(self):
        """Test if view contains all tabs in the group
        and all elements in tabs."""

        utils.create_user_and_authenticate(self)
        group1 = scripts.create_group('test1', 'test1', self.logged_user)
        group2 = scripts.create_group('test2', 'test2', self.logged_user)
        tab_in_group1 = scripts.create_tab('test1', self.logged_user, group1)
        tab_in_group2 = scripts.create_tab('test2', self.logged_user, group2)
        element_in_group1 = scripts.create_element(
            'test1', 'test1', self.logged_user, tab_in_group1
        )
        element_in_group2 = scripts.create_element(
            'test2', 'test2', self.logged_user, tab_in_group2
        )

        response = self.client.get(reverse('group_view', args=(group1.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(tab_in_group1, response.context['tabs_dict'].keys())
        self.assertNotIn(tab_in_group2, response.context['tabs_dict'].keys())
        self.assertIn(
            element_in_group1,
            response.context['tabs_dict'][tab_in_group1]
        )
        self.assertNotIn(
            element_in_group2,
            response.context['tabs_dict'][tab_in_group1]
        )


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

        utils.create_user_and_authenticate(self)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('my_groups_view'))
        self.assertIn(self.logged_user, self.group.users.all())
        self.assertIn(self.group, self.logged_user.joined_groups.all())

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

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_see_only_joined_groups(self):
        """Test if logged user see only joined groups."""

        utils.create_two_users_authenticate_one(self)
        seen = scripts.create_group('seen', 'seen', self.logged_user)
        unseen = scripts.create_group('unseen', 'unseen', self.not_logged_user)

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

        utils.create_user_and_authenticate(self)
        self.group.users.add(self.logged_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('my_groups_view'))
        self.assertNotIn(self.logged_user, self.group.users.all())
        self.assertNotIn(self.group, self.logged_user.joined_groups.all())

    def test_logged_user_not_in_group_is_redirected(self):
        """Test if logged user not in group is redirected."""

        utils.create_user_and_authenticate(self)

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('my_groups_view'))

        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('my_groups_view'))
        self.assertNotIn(self.logged_user, self.group.users.all())
        self.assertNotIn(self.group, self.logged_user.joined_groups.all())

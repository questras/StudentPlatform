from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from ..models import Group
from . import utils_for_testing as utils

User = get_user_model()


class CreateGroupViewTests(TestCase):
    """Tests for CreateGroupView."""

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

        utils.create_user_and_authenticate(self)

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

        utils.create_user_and_authenticate(self)

        data = {'name': 'name'}
        response = self.client.post(reverse('create_group_view'), data)
        self.assertEqual(response.status_code, 400)

        data = {'description': 'description'}
        response = self.client.post(reverse('create_group_view'), data)
        self.assertEqual(response.status_code, 400)


class UpdateGroupViewTests(TestCase):
    """Tests for update_group_view."""

    def test_not_logged_cannot_update(self):
        """Test if not logged user cannot update a group."""

        not_logged_user = utils.create_user('test', 'test')
        group = utils.create_group('test', 'test', not_logged_user)

        update_url = reverse('update_group_view', args=(group.pk,))
        login_url = reverse('login_view')

        response = self.client.get(update_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={update_url}')

        data = {
            'name': 'new',
            'description': 'new',
        }
        response = self.client.post(update_url, data)
        self.assertRedirects(response, expected_url=f'{login_url}?next={update_url}')

    def test_user_not_in_group_cannot_update(self):
        """Test if user who is not in the group cannot update and is
        redirected to my_groups_view."""

        utils.create_two_users_authenticate_one(self)
        group = utils.create_group('test', 'test', self.not_logged_user)

        update_url = reverse('update_group_view', args=(group.pk,))
        groups_url = reverse('my_groups_view')

        response = self.client.get(update_url)
        self.assertRedirects(response, expected_url=groups_url)

        data = {
            'name': 'new',
            'description': 'new',
        }
        response = self.client.post(update_url, data)
        self.assertRedirects(response, expected_url=groups_url)

    def test_not_creator_cannot_update(self):
        """Test if user who is not a creator of group cannot update
        and is redirected to my_groups_view."""

        utils.create_two_users_authenticate_one(self)
        group = utils.create_group('test', 'test', self.not_logged_user)
        group.users.add(self.logged_user)

        update_url = reverse('update_group_view', args=(group.pk,))
        groups_url = reverse('my_groups_view')

        response = self.client.get(update_url)
        self.assertRedirects(response, expected_url=groups_url)

        data = {
            'name': 'new',
            'description': 'new',
        }
        response = self.client.post(update_url, data)
        self.assertRedirects(response, expected_url=groups_url)

    def test_creator_in_group_can_update(self):
        """Test if creator of group who is in it can update."""

        utils.create_user_and_authenticate(self)
        group = utils.create_group('test', 'test', self.user)
        update_url = reverse('update_group_view', args=(group.pk,))
        group_url = reverse('group_view', args=(group.pk,))

        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)

        data = {
            'name': 'new',
            'description': 'new',
        }
        response = self.client.post(update_url, data)
        self.assertRedirects(response, expected_url=group_url)

        updated_group = Group.objects.get(pk=group.pk)
        self.assertEqual(updated_group.name, 'new')
        self.assertEqual(updated_group.description, 'new')

    def test_cannot_update_with_empty_field(self):
        """Test if cannot update group with one or more empty fields"""

        utils.create_user_and_authenticate(self)
        group = utils.create_group('test', 'test', self.user)
        update_url = reverse('update_group_view', args=(group.pk,))

        data_list = [{'name': 'new'}, {'description': 'new'}]
        for data in data_list:
            self.client.post(update_url, data)
            # Group's fields are unchanged.
            self.assertEqual(group.name, 'test')
            self.assertEqual(group.description, 'test')


class DeleteGroupViewTests(TestCase):
    """Tests for DeleteGroupView."""

    def test_not_logged_cannot_delete(self):
        """Test if not logged user cannot delete a group."""

        not_logged_user = utils.create_user('test', 'test')
        group = utils.create_group('test', 'test', not_logged_user)

        delete_url = reverse('delete_group_view', args=(group.pk,))
        login_url = reverse('login_view')

        response = self.client.get(delete_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={delete_url}')

        response = self.client.post(delete_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={delete_url}')
        self.assertEqual(len(Group.objects.all()), 1)

    def test_user_not_in_group_cannot_delete(self):
        """Test if user who is not in the group cannot delete and is
        redirected to my_groups_view."""

        utils.create_two_users_authenticate_one(self)
        group = utils.create_group('test', 'test', self.not_logged_user)

        delete_url = reverse('delete_group_view', args=(group.pk,))
        groups_url = reverse('my_groups_view')

        response = self.client.get(delete_url)
        self.assertRedirects(response, expected_url=groups_url)

        response = self.client.post(delete_url)
        self.assertRedirects(response, expected_url=groups_url)
        self.assertEqual(len(Group.objects.all()), 1)

    def test_not_creator_cannot_delete(self):
        """Test if user who is not a creator of group cannot delete
        and is redirected to my_groups_view."""

        utils.create_two_users_authenticate_one(self)
        group = utils.create_group('test', 'test', self.not_logged_user)
        group.users.add(self.logged_user)

        delete_url = reverse('delete_group_view', args=(group.pk,))
        groups_url = reverse('my_groups_view')

        response = self.client.get(delete_url)
        self.assertRedirects(response, expected_url=groups_url)

        response = self.client.post(delete_url)
        self.assertRedirects(response, expected_url=groups_url)
        self.assertEqual(len(Group.objects.all()), 1)

    def test_creator_in_group_can_delete(self):
        """Test if creator of group who is in it can delete."""

        utils.create_user_and_authenticate(self)
        group = utils.create_group('test', 'test', self.user)
        delete_url = reverse('delete_group_view', args=(group.pk,))
        groups_url = reverse('my_groups_view')

        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(delete_url)
        self.assertRedirects(response, expected_url=groups_url)
        self.assertEqual(len(Group.objects.all()), 0)


class GroupViewTests(TestCase):
    """Tests for group_view."""

    def test_not_logged_user_cannot_access(self):
        """Test if not logged user cannot access the group's view."""

        not_logged_user = utils.create_user('test', 'test')
        group = utils.create_group('test', 'test', not_logged_user)
        login_url = reverse('login_view')
        group_url = reverse('group_view', args=(group.pk,))

        response = self.client.get(group_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={group_url}')

    def test_user_not_in_group_cannot_access(self):
        """Test if user not in the group cannot access
        the group's view."""

        utils.create_two_users_authenticate_one(self)
        group = utils.create_group('test', 'test', self.not_logged_user)

        groups_url = reverse('my_groups_view')
        group_url = reverse('group_view', args=(group.pk,))

        response = self.client.get(group_url)
        self.assertRedirects(response, expected_url=groups_url)

    def test_user_in_group_can_access(self):
        """Test if user in the group can access the group's view."""

        utils.create_two_users_authenticate_one(self)
        group = utils.create_group('test', 'test', self.not_logged_user)
        group.users.add(self.logged_user)

        group_url = reverse('group_view', args=(group.pk,))

        response = self.client.get(group_url)
        self.assertEqual(response.status_code, 200)

    def test_view_contains_all_tabs_and_elements_related_to_group(self):
        """Test if view contains all tabs in the group
        and all elements in tabs."""

        utils.create_user_and_authenticate(self)
        group1 = utils.create_group('test1', 'test1', self.user)
        group2 = utils.create_group('test2', 'test2', self.user)
        tab_in_group1 = utils.create_tab('test1', self.user, group1)
        tab_in_group2 = utils.create_tab('test2', self.user, group2)
        element_in_group1 = utils.create_element(
            'test1', 'test1', self.user, tab_in_group1
        )
        element_in_group2 = utils.create_element(
            'test2', 'test2', self.user, tab_in_group2
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

    def test_not_logged_user_cannot_access(self):
        """Test if not logged user cannot join group."""

        not_logged_user = utils.create_user('test', 'test')
        group = utils.create_group('test', 'test', not_logged_user)

        join_url = reverse('join_group_view', args=(group.pk,))
        login_url = reverse('login_view')

        response = self.client.get(join_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={join_url}')

        response = self.client.post(join_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={join_url}')

    def test_logged_user_can_join(self):
        """Test if logged user can join group."""

        utils.create_two_users_authenticate_one(self)
        group = utils.create_group('test', 'test', self.not_logged_user)
        join_url = reverse('join_group_view', args=(group.pk,))

        response = self.client.get(join_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(join_url)
        self.assertRedirects(response, reverse('my_groups_view'))
        self.assertIn(self.logged_user, group.users.all())
        self.assertIn(group, self.logged_user.joined_groups.all())

    def test_logged_user_already_joined_is_redirected(self):
        """Test if logged user who already joined
        the group is redirected."""

        utils.create_user_and_authenticate(self)
        group = utils.create_group('test', 'test', self.user)
        join_url = reverse('join_group_view', args=(group.pk,))

        response = self.client.get(join_url)
        self.assertRedirects(response, reverse('my_groups_view'))

        response = self.client.post(join_url)
        self.assertRedirects(response, reverse('my_groups_view'))


class MyGroupsViewTests(TestCase):
    """Tests for my_groups_view."""

    def test_not_logged_user_cannot_access(self):
        """Test if not logged user cannot access the view."""

        not_logged_user = utils.create_user('test', 'test')
        utils.create_group('test', 'test', not_logged_user)

        groups_url = reverse('my_groups_view')
        login_url = reverse('login_view')
        response = self.client.get(groups_url)
        self.assertRedirects(response, f'{login_url}?next={groups_url}')

    def test_logged_user_can_access(self):
        """Test if logged user can access the view."""

        utils.create_user_and_authenticate(self)

        response = self.client.get(reverse('my_groups_view'))
        self.assertEqual(response.status_code, 200)

    def test_logged_user_see_only_joined_groups(self):
        """Test if logged user see only joined groups."""

        utils.create_two_users_authenticate_one(self)
        seen_group = utils.create_group('seen', 'seen', self.logged_user)
        unseen_group = utils.create_group('unseen', 'unseen', self.not_logged_user)

        response = self.client.get(reverse('my_groups_view'))
        seen_groups = response.context['groups']
        self.assertEqual(len(seen_groups), 1)
        self.assertIn(seen_group, seen_groups)
        self.assertNotIn(unseen_group, seen_groups)


class LeaveGroupViewTests(TestCase):
    """Tests for leave_group_view"""

    def test_not_logged_user_cannot_leave(self):
        """Test if not logged user cannot leave any group."""

        some_user = utils.create_user('test', 'test')
        group = utils.create_group('test', 'test', some_user)

        leave_url = reverse('leave_group_view', args=(group.pk,))
        login_url = reverse('login_view')

        response = self.client.get(leave_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={leave_url}')

        response = self.client.post(leave_url)
        self.assertRedirects(response, expected_url=f'{login_url}?next={leave_url}')

    def test_logged_user_in_group_can_leave(self):
        """Test if logged user in group can leave it."""

        utils.create_user_and_authenticate(self)
        group = utils.create_group('test', 'test', self.user)
        leave_url = reverse('leave_group_view', args=(group.pk,))

        response = self.client.get(leave_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(leave_url)
        self.assertRedirects(response, reverse('my_groups_view'))
        self.assertNotIn(self.user, group.users.all())
        self.assertNotIn(group, self.user.joined_groups.all())

    def test_logged_user_not_in_group_is_redirected(self):
        """Test if logged user not in group is redirected."""

        utils.create_two_users_authenticate_one(self)
        group = utils.create_group('test', 'test', self.not_logged_user)
        leave_url = reverse('leave_group_view', args=(group.pk,))

        response = self.client.get(leave_url)
        self.assertRedirects(response, reverse('my_groups_view'))

        response = self.client.post(leave_url)
        self.assertRedirects(response, reverse('my_groups_view'))
        self.assertNotIn(self.logged_user, group.users.all())
        self.assertNotIn(group, self.logged_user.joined_groups.all())

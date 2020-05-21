from django.test import TestCase
from django.shortcuts import reverse

from . import utils_for_testing as utils
from .. import scripts
from ..models import Element


def element_test_setup(view_name):
    args = dict()
    args['not_logged_user'] = utils.create_user(
        name='notlogged',
        password='notlogged'
    )
    args['group'] = scripts.create_group(
        name='test',
        description='test',
        user=args['not_logged_user']
    )
    args['tab'] = scripts.create_tab(
        name='test',
        user=args['not_logged_user'],
        group=args['group']
    )
    args['element'] = scripts.create_element(
        name='test',
        text='test',
        user=args['not_logged_user'],
        tab=args['tab']
    )
    args['url'] = reverse(
        view_name,
        args=(args['group'].pk, args['tab'].pk, args['element'].pk,)
    )

    return args


class ElementViewTests(TestCase):
    """Tests for element_view."""

    def setUp(self) -> None:
        self.args = element_test_setup('element_view')

    def test_not_logged_cannot_access(self):
        """Test if not logged user cannot access view."""

        utils.test_not_logged_cannot_access(self, self.args['url'])

    def test_logged_user_not_in_group_cannot_access(self):
        """Test if logged user not in element's group cannot
        access view."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.args['url'], expected_url)

    def test_logged_user_in_group_can_access(self):
        """Test if logged user in element's group can access view."""

        self.client.login(username='notlogged', password='notlogged')
        utils.test_can_access(self, self.args['url'])


# todo: testing with image
class CreateElementViewTests(TestCase):
    """Tests for create_element_view."""

    def setUp(self) -> None:
        self.not_logged_user = utils.create_user('notlogged', 'notlogged')
        self.group = scripts.create_group('test', 'test', self.not_logged_user)
        self.tab = scripts.create_tab('test', self.not_logged_user, self.group)
        self.url = reverse('create_element_view',
                           args=(self.group.pk, self.tab.pk,))
        self.data = {
            'name': 'test',
            'text': 'test',
        }

    def test_not_logged_cannot_access(self):
        """Test if not logged user cannot access view."""

        utils.test_not_logged_cannot_access(self, self.url)

    def test_logged_user_not_in_group_cannot_access(self):
        """Test if logged user not in group cannot access view."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.url, expected_url, self.data)

    def test_logged_user_in_group_can_create_element(self):
        """Test if logged user in group can create new element."""

        utils.create_user_and_authenticate(self)
        self.group.users.add(self.logged_user)
        # 1 is id of created element in the future.
        post_expected_url = reverse('element_view',
                                    args=(self.group.pk, self.tab.pk, 1))

        utils.test_can_access(self, self.url,
                              get_redirect_url=None,
                              post_redirect_url=post_expected_url,
                              data=self.data)
        self.assertEqual(len(Element.objects.all()), 1)

    def test_cannot_create_element_with_empty_field(self):
        """Test if cannot create element with
        empty name or text field."""

        utils.create_user_and_authenticate(self)
        self.group.users.add(self.logged_user)

        data1 = {'name': 'test'}
        data2 = {'text': 'test'}
        data_list = [data1, data2]

        for data in data_list:
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(len(Element.objects.all()), 0)


class UpdateElementViewTests(TestCase):
    """Tests for update_element_view."""

    def setUp(self) -> None:
        self.args = element_test_setup('update_element_view')
        self.data = {
            'name': 'new',
            'text': 'new'
        }

    def test_not_logged_cannot_access(self):
        """Test if not logged user cannot access view."""

        utils.test_not_logged_cannot_access(self, self.args['url'])

    def test_logged_user_not_in_group_cannot_access(self):
        """Test if logged user not in element's group cannot
        access view."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.args['url'], expected_url)

    def test_logged_user_not_creator_cannot_access(self):
        """Test if logged user in element's group who is not
        element's creator cannot access view."""

        utils.create_user_and_authenticate(self)
        self.args['group'].users.add(self.logged_user)
        url_args = (
            self.args['group'].pk, self.args['tab'].pk, self.args['element'].pk,
        )
        expected_url = reverse('element_view', args=url_args)

        utils.test_cannot_access(self, self.args['url'],
                                 expected_url=expected_url,
                                 data=self.data)

        # Object is not updated.
        updated_element = Element.objects.all()[0]
        self.assertEqual(updated_element.name, 'test')
        self.assertEqual(updated_element.text, 'test')
        self.assertIsNone(updated_element.last_edit_date)

    def test_creator_in_group_can_update(self):
        """Test if creator of element who is in element's group can
        update the element."""

        self.client.login(username='notlogged', password='notlogged')
        url_args = (
            self.args['group'].pk, self.args['tab'].pk, self.args['element'].pk,
        )
        expected_url = reverse('element_view', args=url_args)

        utils.test_can_access(self, self.args['url'],
                              get_redirect_url=None,
                              post_redirect_url=expected_url,
                              data=self.data)
        # Object is updated.
        updated_element = Element.objects.all()[0]
        self.assertEqual(updated_element.name, 'new')
        self.assertEqual(updated_element.text, 'new')
        self.assertIsNotNone(updated_element.last_edit_date)

    def test_cannot_update_with_empty_field(self):
        """Test if cannot update element with empty name
        or text field."""

        self.client.login(username='notlogged', password='notlogged')
        data_list = [{'name': 'new'}, {'text': 'new'}]

        for data in data_list:
            response = self.client.post(self.args['url'], data)
            self.assertEqual(response.status_code, 400)
            # Element's fields are unchanged.
            updated_element = Element.objects.all()[0]
            self.assertEqual(updated_element.name, 'test')
            self.assertEqual(updated_element.text, 'test')
            self.assertIsNone(updated_element.last_edit_date)


class DeleteElementViewTests(TestCase):
    """Tests for delete_element_view."""

    def setUp(self) -> None:
        self.args = element_test_setup('delete_element_view')

    def test_not_logged_cannot_access(self):
        """Test if not logged user cannot access view."""

        utils.test_not_logged_cannot_access(self, self.args['url'])

    def test_logged_user_not_in_group_cannot_access(self):
        """Test if logged user not in element's group cannot
        access view."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.args['url'], expected_url)

    def test_logged_user_not_creator_cannot_access(self):
        """Test if logged user in element's group who is not
        element's creator cannot access view."""

        utils.create_user_and_authenticate(self)
        self.args['group'].users.add(self.logged_user)
        url_args = (
            self.args['group'].pk, self.args['tab'].pk, self.args['element'].pk,
        )
        expected_url = reverse('element_view', args=url_args)

        utils.test_cannot_access(self, self.args['url'],
                                 expected_url=expected_url)

        # Object is not deleted.
        self.assertEqual(len(Element.objects.all()), 1)

    def test_creator_in_group_can_delete(self):
        """Test if creator of element who is in element's group can
        delete the element and is redirected to element's group view."""

        self.client.login(username='notlogged', password='notlogged')
        expected_url = reverse('group_view', args=(self.args['group'].pk,))

        utils.test_can_access(self, self.args['url'],
                              get_redirect_url=None,
                              post_redirect_url=expected_url)
        # Object is deleted.
        self.assertEqual(len(Element.objects.all()), 0)

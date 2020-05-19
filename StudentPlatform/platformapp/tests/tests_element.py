from django.test import TestCase
from django.shortcuts import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from . import utils_for_testing as utils
from .. import scripts
from ..models import Group, Tab, Element


class ElementViewTests(TestCase):
    """Tests for element_view."""

    def setUp(self) -> None:
        self.not_logged_user = utils.create_user('notlogged', 'notlogged')
        self.group = scripts.create_group('test', 'test', self.not_logged_user)
        self.tab = scripts.create_tab('test', self.not_logged_user, self.group)
        self.element = scripts.create_element('test', 'test',
                                              self.not_logged_user, self.tab)
        self.url = reverse('element_view',
                           args=(self.group.pk, self.tab.pk, self.element.pk,))

    def test_not_logged_cannot_access(self):
        """Test if not logged user cannot access view."""

        utils.test_not_logged_cannot_access(self, self.url)

    def test_logged_user_not_in_group_cannot_access(self):
        """Test if logged user not in element's group cannot
        access view."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.url, expected_url)

    def test_logged_user_in_group_can_access(self):
        """Test if logged user in element's group can access view."""

        self.client.login(username='notlogged', password='notlogged')
        utils.test_can_access(self, self.url)


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
        post_expected_url = reverse('group_view', args=(self.group.pk,))

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

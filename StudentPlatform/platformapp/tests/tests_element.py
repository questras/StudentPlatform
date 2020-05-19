from django.test import TestCase
from django.shortcuts import reverse

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


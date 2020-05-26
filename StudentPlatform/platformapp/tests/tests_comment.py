from django.test import TestCase
from django.shortcuts import reverse

from ..models import Comment
from . import utils_for_testing as utils
from .. import scripts


class AddCommentViewTests(TestCase):
    """Tests for add_comment_view."""

    def setUp(self) -> None:
        self.not_logged_user = scripts.create_user('notlogged', 'notlogged')
        self.group = scripts.create_group('test', 'test', self.not_logged_user)
        self.tab = scripts.create_tab('test', self.not_logged_user, self.group)
        self.element = scripts.create_element('test', 'test',
                                              self.not_logged_user, self.tab)
        url_args = (self.group.pk, self.tab.pk, self.element.pk,)
        self.url = reverse('add_comment_view', args=url_args)
        self.data = {
            'text': 'test',
        }

    def test_not_logged_cannot_add_comment(self):
        """Test if not logged user cannot add comment."""

        utils.test_not_logged_cannot_access(self, self.url, data=self.data)

    def test_logged_not_in_group_cannot_add_comment(self):
        """Test if logged user not in element's group cannot
        add comment."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.url,
                                 expected_url=expected_url,
                                 data=self.data)

    def test_logged_in_group_can_add_comment(self):
        """Test if logged user in element's group can add comment."""

        utils.create_user_and_authenticate(self)
        self.group.users.add(self.logged_user)
        url_args = (self.group.pk, self.tab.pk, self.element.pk,)
        expected_url = reverse('element_view', args=url_args)

        utils.test_can_access(self, self.url,
                              get_redirect_url=expected_url,
                              post_redirect_url=expected_url,
                              data=self.data)
        self.assertEqual(len(Comment.objects.all()), 1)

    def test_cannot_add_comment_with_empty_field(self):
        """Test if cannot add comment with empty text field."""

        utils.create_user_and_authenticate(self)
        self.group.users.add(self.logged_user)
        fields = ['text']

        utils.test_cannot_post_with_empty_fields(self, self.url, fields)

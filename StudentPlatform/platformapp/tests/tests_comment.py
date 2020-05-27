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
        self.url = reverse('add_comment_view', args=(self.element.pk,))
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
        expected_url = reverse('element_view', args=(self.element.pk,))

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


class DeleteCommentViewTests(TestCase):
    """Tests for delete_comment_view."""

    def setUp(self) -> None:
        self.not_logged_user = scripts.create_user('notlogged', 'notlogged')
        self.group = scripts.create_group('test', 'test', self.not_logged_user)
        self.tab = scripts.create_tab('test', self.not_logged_user, self.group)
        self.element = scripts.create_element('test', 'test',
                                              self.not_logged_user, self.tab)
        self.comment = scripts.create_comment('test', self.not_logged_user,
                                              self.element)
        self.url = reverse('delete_comment_view', args=(self.comment.pk,))

    def test_not_logged_cannot_delete_comment(self):
        """Test if not logged user cannot delete comment."""

        utils.test_not_logged_cannot_access(self, self.url)

    def test_logged_not_in_group_cannot_delete_comment(self):
        """Test if logged in user not in comment's group
        cannot delete the comment."""

        utils.create_user_and_authenticate(self)
        expected_url = reverse('my_groups_view')

        utils.test_cannot_access(self, self.url, expected_url)

    def test_logged_in_group_not_creator_cannot_delete_comment(self):
        """Test if logged user in comment's group who is not
        comment's creator cannot delete the comment."""

        utils.create_user_and_authenticate(self)
        self.group.users.add(self.logged_user)
        expected_url = reverse('element_view', args=(self.element.pk,))

        utils.test_cannot_access(self, self.url, expected_url)

    def test_creator_in_group_can_delete_comment(self):
        """Test if creator of the comment can delete it."""

        self.client.login(username='notlogged', password='notlogged')
        expected_url = reverse('element_view', args=(self.element.pk,))

        self.assertEqual(len(Comment.objects.all()), 1)
        utils.test_can_access(self, self.url, post_redirect_url=expected_url)
        self.assertEqual(len(Comment.objects.all()), 0)

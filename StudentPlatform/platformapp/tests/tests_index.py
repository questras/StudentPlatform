from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from . import utils_for_testing as utils
from .. import scripts

User = get_user_model()


class IndexViewTests(TestCase):
    """Tests for index_view"""

    def setUp(self) -> None:
        self.url = reverse('index_view')

    def test_not_logged_user_can_access_index_view(self):
        """Test if not logged user can access index_view"""

        utils.test_can_access(self, self.url)

    def test_logged_user_is_redirected_to_feed(self):
        """Test if logged user is redirected to feed_view"""

        utils.create_user_and_authenticate(self)

        response = self.client.get(self.url)
        self.assertRedirects(response, expected_url=reverse('feed_view'))


class FeedViewTests(TestCase):
    """Tests for feed_view."""

    def setUp(self) -> None:
        self.url = reverse('feed_view')

    def test_not_logged_user_cannot_access(self):
        """Test if not logged user cannot access the view."""

        utils.test_not_logged_cannot_access(self, self.url)

    def test_logged_user_can_access(self):
        """Test if logged user can access the view"""

        utils.create_user_and_authenticate(self)
        utils.test_can_access(self, self.url)

    def test_only_related_objects_are_visible(self):
        """Test if user sees only feed posts related to his
        groups and groups' tabs, elements and comments."""

        other_user = scripts.create_user('other', 'other')
        logged_user = utils.create_user_and_authenticate(self)

        seen_group = scripts.create_group('seen', 'seen', other_user)
        seen_group.users.add(logged_user)
        unseen_group = scripts.create_group('unseen', 'unseen', other_user)

        seen_tab = scripts.create_tab('seen', other_user, seen_group)
        unseen_tab = scripts.create_tab('unseen', other_user, unseen_group)

        seen_element = scripts.create_element('seen', 'test',
                                              other_user, seen_tab)
        unseen_element = scripts.create_element('unseen', 'test',
                                                other_user, unseen_tab)

        seen_comment = scripts.create_comment('seen', other_user,
                                              seen_element)
        unseen_comment = scripts.create_comment('unseen', other_user,
                                                unseen_element)
        seen_objects = [seen_tab, seen_element, seen_comment]
        unseen_objects = [unseen_tab, unseen_element, unseen_comment]

        response = self.client.get(self.url)
        objects = [obj[0] for obj in response.context['entries']]
        for o in seen_objects:
            self.assertIn(o, objects)
        for o in unseen_objects:
            self.assertNotIn(o, objects)


class HowToViewTests(TestCase):
    """Tests for how_to_view."""

    def setUp(self) -> None:
        self.url = reverse('how_to_view')

    def test_not_logged_user_can_access(self):
        """Test if not logged user can access."""

        utils.test_can_access(self, self.url)

    def test_logged_user_can_access(self):
        """Test if logged user can access."""

        utils.create_user_and_authenticate(self)
        utils.test_can_access(self, self.url)

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Group, UserGroupRelation, Tab
from django.contrib.auth import get_user_model

User = get_user_model()


def login_user(self, superuser=False):
    """Create user or superuser and log in for testing purposes"""
    if superuser:
        self.user = User.objects.create_superuser(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
    else:
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')


def redirect_next(url1, url2):
    """Return redirect url with 'next' attribute"""
    return '{}?next={}'.format(reverse(url1), reverse(url2))


def create_group(creator):
    """Create group for test purposes"""
    group = Group(
        name='t',
        description='t',
        creator=creator,
        share_url='placeholder.com'
    )
    group.save()
    group.share_url = reverse('join_group_view', args=(group.id,))
    group.save()

    UserGroupRelation(group=group, user=creator).save()
    return group


def create_tab(creator, group):
    """Create tab for test purposes"""
    tab = Tab(
        name='t',
        creator=creator,
        group=group,
    )
    tab.save()
    return tab


def activate_group(self, group):
    """Activate group for test purposes"""
    self.client.post(reverse('activate_group', args=(group.id,)))


class IndexViewTests(TestCase):
    """Tests related to Index view"""

    def test_logged_in(self):
        """
        Test: logged in user can access Index view and sees his username
        in the top right corner
         """
        login_user(self)
        response = self.client.get(reverse('index'))

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_not_logged_in(self):
        """
        Test: not logged user can access Index view and sees
        'You need to be logged in' information
         """
        response = self.client.get(reverse('index'))

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'You need to be logged in')


class SignUpViewTests(TestCase):
    """Tests related to SignUp view"""

    def test_logged_in_cannot_sign_up(self):
        """Test: logged in user cannot sign up"""
        login_user(self)
        response = self.client.get(reverse('signup'))

        self.assertRedirects(response, expected_url=reverse('index'))

    def test_not_logged_in_can_sign_up(self):
        """
        Test: not logged in user can sign up
        """
        response = self.client.get(reverse('signup'))
        self.assertEquals(response.status_code, 200)

        response = self.client.post(
            reverse('signup'),
            {
                'username': 'testuser',
                'first_name': 'testuser',
                'last_name': 'testuser',
                'email': 'testuser@testuser.com',
                'password1': 'iamtesting123',
                'password2': 'iamtesting123',
            }
        )
        self.assertRedirects(response, expected_url=reverse('login'))
        self.assertEquals(len(User.objects.all()), 1)

    def test_cannot_sign_up_existing_username_or_email(self):
        """Test: user cannot sign up with existing username or email"""
        User.objects.create_user(
            username='testuser',
            password='12345',
            email='testuser@testuser.com'
        ).save()

        response = self.client.get(reverse('signup'))
        self.assertEquals(response.status_code, 200)

        response = self.client.post(
            reverse('signup'),
            {
                'username': 'testuser',
                'first_name': 'testuser',
                'last_name': 'testuser',
                'email': 'notthesame@testuser.com',
                'password1': 'iamtesting123',
                'password2': 'iamtesting123',
            }
        )
        self.assertEquals(response.status_code, 200)  # no redirect code
        self.assertEquals(len(User.objects.all()), 1)  # exists only one user created earlier

        response = self.client.post(
            reverse('signup'),
            {
                'username': 'notthesame',
                'first_name': 'testuser',
                'last_name': 'testuser',
                'email': 'testuser@testuser.com',
                'password1': 'iamtesting123',
                'password2': 'iamtesting123',
            }
        )
        self.assertEquals(response.status_code, 200)  # no redirect code
        self.assertEquals(len(User.objects.all()), 1)  # exists only one user created earlier


class LoginViewTests(TestCase):
    def test_logged_in_user_cannot_login(self):
        """Test: logged in user cannot access Login view"""
        login_user(self)

        response = self.client.get(reverse('login'))
        self.assertRedirects(response, expected_url=reverse('index'))

    def test_not_logged_in_user_can_login(self):
        """Test: not logged in user can access Login view and log in"""
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)

        User.objects.create_user(username='testuser', password='12345').save()
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})

        self.assertRedirects(response, expected_url=reverse('index'))


class CreateGroupTests(TestCase):
    """Tests related to Create Group view"""

    def test_not_logged_in_cannot_access(self):
        """Test: not logged in user cannot access Create Group view"""
        response = self.client.get(reverse('create_group'))
        self.assertRedirects(response, expected_url=redirect_next('login', 'create_group'))

    def test_cannot_create_group_with_empty_field(self):
        """Test: cannot create group with one or more empty fields"""
        login_user(self)
        response = self.client.get(reverse('create_group'))
        self.assertEquals(response.status_code, 200)

        response = self.client.post(reverse('create_group'), {'name': 'group_name'})
        self.assertNotEquals(response.status_code, 302)  # no redirect code

        response = self.client.post(reverse('create_group'), {'description': 'group_desc'})
        self.assertNotEquals(response.status_code, 302)  # no redirect code

    def test_user_can_create_group(self):
        """Test: user can create group"""
        login_user(self)
        response = self.client.get(reverse('create_group'))
        self.assertEquals(response.status_code, 200)

        response = self.client.post(reverse('create_group'), {'name': 'n', 'description': 'd'})
        self.assertRedirects(response,
                             expected_url=reverse('groups_view'))

        created_group = Group.objects.all()
        self.assertEquals(len(created_group), 1)  # contains one group just created

        created_group = created_group[0]

        self.assertEquals(created_group.name, 'n')
        self.assertEquals(created_group.description, 'd')
        self.assertEquals(created_group.creator, self.user)
        self.assertEquals(created_group.share_url, reverse('join_group_view', args=(created_group.id,)))

        relation = UserGroupRelation.objects.all()
        self.assertEquals(len(relation), 1)  # contains one relation just created

        relation = relation[0]
        self.assertEquals(relation.group, created_group)
        self.assertEquals(relation.user, created_group.creator)


class GroupsViewTests(TestCase):
    """Tests related to Groups view"""

    def test_not_logged_in_cannot_access(self):
        """Test: not logged in user is redirected, logged in user can access the view"""
        response = self.client.get(reverse('groups_view'))
        self.assertRedirects(response, expected_url=redirect_next('login', 'groups_view'))

        login_user(self)
        response = self.client.get(reverse('groups_view'))
        self.assertEquals(response.status_code, 200)

    def test_users_sees_their_groups(self):
        """Test: user sees groups he belongs to, and no other ones"""
        login_user(self)

        # create different user and create group unseen for logged user
        diff_user = User.objects.create_user(username='difftestuser', password='12345')
        unseen_group = create_group(diff_user)

        response = self.client.get(reverse('groups_view'))
        groups = response.context['groups']
        self.assertEquals(len(groups), 0)  # logged user should not see any groups

        # create seen group
        seen_group = create_group(self.user)

        response = self.client.get(reverse('groups_view'))
        groups = response.context['groups']
        self.assertEquals(len(groups), 1)  # logged user should see only 1 group
        self.assertTrue(seen_group in groups)
        self.assertTrue(unseen_group not in groups)


class ActivateGroupTests(TestCase):
    """Tests related to activate_group view"""

    def test_access_to_view(self):
        """
        Test: not logged in user is redirected,
        logged in user who is in the group can access the view
        """
        # create different user and create group unseen for logged user
        diff_user = User.objects.create_user(username='difftestuser', password='12345')
        unseen_group = create_group(diff_user)

        # activate group: not logged in user
        response = self.client.post(reverse('activate_group', args=(unseen_group.id,)))
        url1 = reverse('login')
        url2 = reverse('activate_group', args=(unseen_group.id,))
        expected_url = '{}?next={}'.format(url1, url2)
        self.assertRedirects(response, expected_url=expected_url)

        login_user(self)

        # activate group: user not belonging to group
        response = self.client.get(reverse('activate_group', args=(unseen_group.id,)))
        self.assertRedirects(response, expected_url=reverse('groups_view'))

        # create seen group
        seen_group = create_group(self.user)

        # activate group: user belonging to group
        response = self.client.get(reverse('activate_group', args=(seen_group.id,)))
        self.assertRedirects(response, expected_url=reverse('group_main'))

    def test_sidebar_seen_when_group_activated(self):
        """
        Test: user sees sidebar when a groups is activated,
         doesn't see it otherwise
        """
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'sidebar-sticky')

        login_user(self)
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'sidebar-sticky')

        group = create_group(self.user)
        self.client.post(reverse('activate_group', args=(group.id,)))
        response = self.client.get(reverse('index'))

        self.assertContains(response, 'sidebar-sticky')

    def test_session_variable_after_clicking_group(self):
        """Test: session variable is changed to clicked group"""
        login_user(self)
        group = create_group(self.user)
        response = self.client.post(reverse('activate_group', args=(group.id,)))

        self.assertRedirects(response, expected_url=reverse('group_main'))
        self.assertEquals(self.client.session['group'], group.id)

    def test_group_and_tabs_in_context(self):
        """Test: current group and tabs are in context"""
        # None when user is not logged in
        response = self.client.get(reverse('index'))
        self.assertTrue(response.context['group'] is None)
        self.assertTrue(response.context['tabs'] is None)

        # None when user is logged in but no group is activated
        login_user(self)
        response = self.client.get(reverse('index'))
        self.assertTrue(response.context['group'] is None)
        self.assertTrue(response.context['tabs'] is None)

        group = create_group(self.user)
        tab = create_tab(self.user, group)
        self.client.post(reverse('activate_group', args=(group.id,)))

        # When user is logged in and has activated group
        response = self.client.get(reverse('index'))
        self.assertTrue(response.context['group'] == group)
        self.assertTrue(tab in response.context['tabs'])


class CreateTabTests(TestCase):
    """Tests related to create_tab view"""

    def test_access_to_view(self):
        """Test: only accessable when group is activated"""
        # not logged in
        response = self.client.get(reverse('create_tab'))
        self.assertRedirects(response, expected_url=redirect_next('login', 'create_tab'))

        # logged in no group activated
        login_user(self)
        response = self.client.get(reverse('create_tab'))
        self.assertRedirects(response, expected_url=reverse('groups_view'))

        # logged in group activated
        group = create_group(self.user)
        activate_group(self, group)
        response = self.client.get(reverse('create_tab'))
        self.assertEquals(response.status_code, 200)

    def test_user_can_create_tab(self):
        """Test: user can create tab"""
        login_user(self)
        group = create_group(self.user)

        session = self.client.session
        session['group'] = group.id
        session.save()

        response = self.client.post(reverse('create_tab'), {'name': 'n'})
        self.assertRedirects(response, expected_url=reverse('group_main'))

        created_tabs = Tab.objects.all()
        self.assertEquals(len(created_tabs), 1)  # contains one tab just created

        created_tab = created_tabs[0]
        self.assertEquals(created_tab.name, 'n')
        self.assertEquals(created_tab.group, group)
        self.assertEquals(created_tab.creator, self.user)


class GroupMainViewTests(TestCase):
    """Tests related to group_main view"""

    def test_access_to_view(self):
        """
        Test: cannot access view when: not logged or
        group is not activated, can otherwise
        """
        # not logged in
        response = self.client.get(reverse('group_main'))
        self.assertRedirects(response, expected_url=redirect_next('login', 'group_main'))

        login_user(self)
        group = create_group(self.user)

        # not activated group
        response = self.client.get(reverse('group_main'))
        self.assertRedirects(response, expected_url=reverse('groups_view'))

        # activated group
        activate_group(self, group)

        response = self.client.get(reverse('group_main'))
        self.assertEquals(response.status_code, 200)

    def test_contains_group_details(self):
        """Test: view contains group's name, description, creator, leave button"""
        login_user(self)
        group = create_group(self.user)
        activate_group(self, group)

        response = self.client.get(reverse('group_main'))
        self.assertContains(response, group.name)
        self.assertContains(response, group.description)
        self.assertContains(response, group.creator.get_full_name())
        self.assertContains(response, '<button class="btn btn-warning">Leave Group</button>')


class JoinGroupViewTests(TestCase):
    """Tests related to join_group_view."""

    def test_access_to_view(self):
        """Test: only logged in user who is not in this group can access join_group_view."""
        diff_user = User.objects.create_user(username='difftestuser', password='12345')
        group = create_group(diff_user)

        # not logged in
        response = self.client.get(reverse('join_group_view', args=(group.id,)))
        self.assertEquals(response.status_code, 302)  # redirect code

        # logged in
        login_user(self)
        response = self.client.get(reverse('join_group_view', args=(group.id,)))
        self.assertEquals(response.status_code, 200)

        # already in group
        group = create_group(self.user)
        response = self.client.get(reverse('join_group_view', args=(group.id,)))
        self.assertRedirects(
            response,
            expected_url=reverse('activate_group', args=(group.id,)),
            target_status_code=302
        )

    def test_contains_correct_elements(self):
        """Test: join_group_view contains group's name and button to join and cancel"""
        diff_user = User.objects.create_user(username='difftestuser', password='12345')
        group = create_group(diff_user)

        login_user(self)
        response = self.client.get(reverse('join_group_view', args=(group.id,)))
        self.assertContains(response, group.name)
        self.assertContains(response, group.description)
        self.assertContains(response, group.creator.get_full_name())
        self.assertContains(response, '<button class="btn btn-success">Join</button>')
        self.assertContains(response, '<button class="btn btn-danger">Cancel</button>')


class JoinGroupTests(TestCase):
    """Tests related to join_group functionality"""

    def test_user_added_to_group(self):
        """Test: user is added to group."""
        diff_user = User.objects.create_user(username='difftestuser', password='12345')
        group = create_group(diff_user)

        login_user(self)
        self.client.post(reverse('join_group', args=(group.id,)))

        relations = UserGroupRelation.objects.all()
        self.assertEquals(len(relations), 2)  # new relation and creator relation

        relation = relations[1]
        self.assertEquals(relation.group, group)
        self.assertEquals(relation.user, self.user)

    def test_user_redirected_to_activate_group(self):
        """Test: user is redirected to activate_group of joined group."""
        diff_user = User.objects.create_user(username='difftestuser', password='12345')
        group = create_group(diff_user)

        login_user(self)
        response = self.client.post(reverse('join_group', args=(group.id,)))
        self.assertRedirects(
            response,
            expected_url=reverse('activate_group', args=(group.id,)),
            target_status_code=302
        )


class SearchGroupView(TestCase):
    """Tests related to search_group view"""

    def test_access_to_view(self):
        """Test: not logged users do not have access"""
        # not logged
        response = self.client.get(reverse('search_group'))
        self.assertRedirects(response, expected_url=redirect_next('login', 'search_group'))

        # logged in
        login_user(self)
        response = self.client.get(reverse('search_group'))
        self.assertEquals(response.status_code, 200)

    def test_page_content(self):
        """Test: correct page content."""
        login_user(self)
        response = self.client.get(reverse('search_group'))

        # No group searched for
        self.assertContains(response, 'class="btn btn-primary"')
        self.assertNotContains(response, '<table class="table table-striped table-sm">')

        # Group searched for
        group = create_group(self.user)
        response = self.client.post(reverse('search_group'), {'search_query': 't'})
        self.assertContains(response, 'class="btn btn-primary"')
        self.assertContains(response, '<table class="table table-striped table-sm">')
        self.assertTrue(group in response.context['search_result'])

        # No group found
        response = self.client.post(reverse('search_group'), {'search_query': 'ssss'})
        self.assertNotContains(response, '<table class="table table-striped table-sm">')
        self.assertContains(response, 'No results')

    def test_searching_for_groups(self):
        """Test: specific groups shown when searching and others not."""
        login_user(self)
        user1 = User.objects.create_user(
            username='diff',
            password='12345',
            first_name='aleks',
            last_name='skela')

        user2 = User.objects.create_user(
            username='ffid',
            password='12345',
            first_name='george',
            last_name='egroeg')

        group1 = Group(
            name='g1',
            description='desc1',
            creator=user1,
            share_url='placeholder.com'
        )
        group1.save()

        group2 = Group(
            name='abc2',
            description='csed1',
            creator=user2,
            share_url='placeholder.com'
        )
        group2.save()

        # queries regarding both groups
        response = self.client.post(reverse('search_group'), {'search_query': 'sss'})
        context = response.context['search_result']
        self.assertTrue(group1 not in context)
        self.assertTrue(group2 not in context)

        response = self.client.post(reverse('search_group'), {'search_query': '1'})
        context = response.context['search_result']
        self.assertTrue(group1 in context)
        self.assertTrue(group2 in context)

        # search by names
        response = self.client.post(reverse('search_group'), {'search_query': 'g1'})
        context = response.context['search_result']
        self.assertTrue(group1 in context)
        self.assertTrue(group2 not in context)

        response = self.client.post(reverse('search_group'), {'search_query': 'abc'})
        context = response.context['search_result']
        self.assertTrue(group1 not in context)
        self.assertTrue(group2 in context)

        # search by description
        response = self.client.post(reverse('search_group'), {'search_query': 'desc'})
        context = response.context['search_result']
        self.assertTrue(group1 in context)
        self.assertTrue(group2 not in context)

        response = self.client.post(reverse('search_group'), {'search_query': 'csed'})
        context = response.context['search_result']
        self.assertTrue(group1 not in context)
        self.assertTrue(group2 in context)

        # search by creator's first and last name
        response = self.client.post(reverse('search_group'), {'search_query': 'aleks'})
        context = response.context['search_result']
        self.assertTrue(group1 in context)
        self.assertTrue(group2 not in context)

        response = self.client.post(reverse('search_group'), {'search_query': 'skela'})
        context = response.context['search_result']
        self.assertTrue(group1 in context)
        self.assertTrue(group2 not in context)

        response = self.client.post(reverse('search_group'), {'search_query': 'george'})
        context = response.context['search_result']
        self.assertTrue(group1 not in context)
        self.assertTrue(group2 in context)

        response = self.client.post(reverse('search_group'), {'search_query': 'egroeg'})
        context = response.context['search_result']
        self.assertTrue(group1 not in context)
        self.assertTrue(group2 in context)

        # cannot search by username
        response = self.client.post(reverse('search_group'), {'search_query': 'diff'})
        context = response.context['search_result']
        self.assertTrue(group1 not in context)
        self.assertTrue(group2 not in context)

        response = self.client.post(reverse('search_group'), {'search_query': 'ffid'})
        context = response.context['search_result']
        self.assertTrue(group1 not in context)
        self.assertTrue(group2 not in context)


"""
search group tests:
- no table when no post request
- group with key word shown: compare to name, description, creator
- groups without keyword not shown
"""

"""
tab page tests:
access to view: only if group activated, cannot otherwise
elements in view: create element for all, delete tab and edit tab button only for creator
elements in this tab seen, others not

"""

"""
comments tests:
comments seen
comments can be created (if group activated and logged in)
"""

"""
delete tab tests:
not-logged/not owner cannot access
owner can access if session is ok
tab is actually deleted
"""

"""
create element tests:
not-logged cannot access
logged can access if session is not -1
form cannot be submitted with empty(required) fields
"""

"""
delete element tests:
not-logged/not owner cannot access
owner can access if session is ok
element is actually deleted
"""

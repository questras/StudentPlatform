from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from platformapp.forms import RegistrationForm, CreateGroupForm
from platformapp.forms import CreateTabForm
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, get_user_model
from .models import Group, UserGroupRelation, Tab, Element

User = get_user_model()


def get_current_group(request):
    """
    Return session's current group or None if not yet set.
    Used to store data in context for group's sidebar.
    """
    try:
        curr_group = request.session['group']
    except KeyError:
        request.session['group'] = -1  # Set group id as -1 (no group)
        curr_group = -1

    if curr_group == -1:
        return None
    else:
        return Group.objects.get(pk=curr_group)


def get_current_tabs(group):
    """
    Return group's tabs or None if group is None.
    Used to store data in context for group's sidebar.
    """
    if group:
        return list(Tab.objects.filter(group=group))
    else:
        return None


def index(request):
    """Index view of the page."""
    group = get_current_group(request)
    tabs = get_current_tabs(group)

    context = {
        'group': group,
        'tabs': tabs,
    }
    return render(request, 'platformapp/index.html', context)


class SignUp(generic.CreateView):
    """A view to register an user"""
    form_class = RegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'platformapp/signup.html'

    def get(self, request, *args, **kwargs):
        """Redirect to index if logged user tries to sign up"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('index'))
        return super(SignUp, self).get(request, *args, **kwargs)


@login_required
def logout_view(request):
    """A view to logout."""
    request.session['group'] = -1  # Reset current group's id
    logout(request)

    return HttpResponseRedirect(reverse_lazy('index'))


@login_required
def create_group(request):
    """A view to create a group"""
    # when user tries to create a group
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            creator = request.user

            group = Group(
                name=name,
                description=description,
                creator=creator,
                share_url='placeholder.com'
            )
            # change share_url based on group's id
            group.save()
            group.share_url = reverse('join_group_view', args=(group.id,))
            group.save()

            UserGroupRelation(user=creator, group=group).save()

            return HttpResponseRedirect(reverse_lazy('groups_view'))
    # when user opens view
    else:
        form = CreateGroupForm

    group = get_current_group(request)
    tabs = get_current_tabs(group)

    context = {
        'form': form,
        'group': group,
        'tabs': tabs,
    }

    return render(request, 'platformapp/create_group.html', context)


@login_required
def groups_view(request):
    """A view where users see their groups"""
    # get all groups which current user belongs to
    groups_ids = UserGroupRelation.objects.filter(user=request.user).values_list('group', flat=True)
    groups = Group.objects.filter(pk__in=list(groups_ids))

    group = get_current_group(request)
    tabs = get_current_tabs(group)

    context = {
        'groups': list(groups),
        'group': group,
        'tabs': tabs,
    }

    return render(request, 'platformapp/groups_view.html', context)


@login_required
def activate_group(request, group_id):
    """Activate group clicked by user"""
    # check if user belongs to the group
    group = Group.objects.get(pk=group_id)
    relation = UserGroupRelation.objects.filter(group=group, user=request.user)

    if not relation:
        return HttpResponseRedirect(reverse_lazy('groups_view'))
    else:
        request.session['group'] = group_id
        return HttpResponseRedirect(reverse_lazy('group_main'))


@login_required
def create_tab(request):
    """A view to create a tab."""
    group = get_current_group(request)
    if group is None:
        return HttpResponseRedirect(reverse_lazy('groups_view'))

    # when user tries to create a tab
    if request.method == 'POST':
        form = CreateTabForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            creator = request.user
            tab = Tab(name=name, creator=creator, group=group)
            tab.save()

            return HttpResponseRedirect(reverse_lazy('group_main'))
    # when user opens view
    else:
        form = CreateTabForm

    group = get_current_group(request)
    tabs = get_current_tabs(group)

    context = {
        'form': form,
        'group': group,
        'tabs': tabs,
    }

    return render(request, 'platformapp/create_tab.html', context)


@login_required
def group_main(request):
    group = get_current_group(request)
    if group is None:
        return HttpResponseRedirect(reverse_lazy('groups_view'))

    tabs = get_current_tabs(group)
    context = {
        'group': group,
        'tabs': tabs,
    }

    return render(request, 'platformapp/group_main.html', context)


@login_required
def join_group_view(request, join_group_id):
    """A view to join a group."""
    group_to_join = get_object_or_404(Group, pk=join_group_id)

    # redirect if user already in this relation
    existing_relation = UserGroupRelation.objects.filter(group=group_to_join, user=request.user)
    if existing_relation:
        return HttpResponseRedirect(reverse('activate_group', args=(join_group_id,)))

    group = get_current_group(request)
    tabs = get_current_tabs(group)

    context = {
        'group_to_join': group_to_join,
        'group': group,
        'tabs': tabs,
    }

    return render(request, 'platformapp/join_group_view.html', context)


@login_required
def join_group(request, join_group_id):
    """Functionality to join a group."""
    group_to_join = get_object_or_404(Group, pk=join_group_id)

    # redirect if user already in this relation
    existing_relation = UserGroupRelation.objects.filter(group=group_to_join, user=request.user)
    if existing_relation:
        return HttpResponseRedirect(reverse('activate_group', args=(join_group_id,)))

    relation = UserGroupRelation(user=request.user, group=group_to_join)
    relation.save()

    return HttpResponseRedirect(reverse('activate_group', args=(join_group_id,)))


@login_required
def search_group(request):
    """A view to search for a group"""
    group = get_current_group(request)
    tabs = get_current_tabs(group)
    context = {
        'group': group,
        'tabs': tabs,
    }

    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')

        if search_query == '':
            return render(request, 'platformapp/search_group.html', context)

        found_groups = []
        # search for name
        for g in list(Group.objects.filter(name__contains=search_query)):
            if g not in found_groups:
                found_groups.append(g)

        # search for description
        for g in list(Group.objects.filter(description__contains=search_query)):
            if g not in found_groups:
                found_groups.append(g)

        # search for creator's first name
        users = list(User.objects.filter(first_name=search_query))
        for user in users:
            for g in list(Group.objects.filter(creator=user)):
                if g not in found_groups:
                    found_groups.append(g)

        # search for creator's last name
        users = list(User.objects.filter(last_name=search_query))
        for user in users:
            for g in list(Group.objects.filter(creator=user)):
                if g not in found_groups:
                    found_groups.append(g)

        context['search_result'] = found_groups

    return render(request, 'platformapp/search_group.html', context)


@login_required
def leave_group(request, leaving_group_id):
    """A functionality to leave group"""
    session_group = get_current_group(request)

    if session_group is not None and session_group.id == leaving_group_id:
        relation = UserGroupRelation.objects.filter(group=leaving_group_id, user=request.user)
        relation.delete()
        request.session['group'] = -1

    return HttpResponseRedirect(reverse_lazy('groups_view'))


@login_required
def delete_tab(request, deleting_tab_id):
    """A functionality to delete tab"""
    session_group = get_current_group(request)

    if session_group is None:
        return HttpResponseRedirect(reverse_lazy('groups_view'))
    else:
        tab = get_object_or_404(Tab, pk=deleting_tab_id)
        if tab.creator == request.user and tab.group == session_group:
            tab.delete()
            return HttpResponseRedirect(reverse_lazy('group_main'))
        elif tab.group != session_group:
            return HttpResponseRedirect(reverse_lazy('groups_view'))
        else:
            return HttpResponseRedirect(reverse_lazy('group_main'))


@login_required
def tab_view(request, tab_id):
    """A view of a Tab"""
    session_group = get_current_group(request)
    session_tabs = get_current_tabs(session_group)

    if session_group is None:
        return HttpResponseRedirect(reverse_lazy('groups_view'))
    else:
        tab = get_object_or_404(Tab, pk=tab_id)  # get requested tab
        if tab.group != session_group:
            return HttpResponseRedirect(reverse_lazy('groups_view'))
        else:
            elements = list(Element.objects.filter(tab=tab))
            context = {
                'group': session_group,
                'tabs': session_tabs,
                'tab': tab,
                'elements': elements,
            }

            return render(request, 'platformapp/tab_view.html', context)

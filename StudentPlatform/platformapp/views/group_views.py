from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import reverse, render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone

from ..models import Group, Tab, Element
from ..forms import CreateGroupForm, UpdateGroupForm


class CreateGroupView(LoginRequiredMixin, CreateView):
    """A view for creating new groups."""

    login_url = reverse_lazy('login_view')
    redirect_field_name = 'next'

    model = Group
    form_class = CreateGroupForm
    template_name = 'platformapp/create_group_view.html'
    success_url = reverse_lazy('my_groups_view')

    def form_valid(self, form):
        """Validate form with current user as group's creator."""

        group = form.save(commit=False)
        group.creator = self.request.user
        group.save()
        group.users.add(self.request.user)
        group.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        """Return 400 status code when form is invalid."""

        response = super().form_invalid(form)
        response.status_code = 400
        return response


@login_required
def update_group_view(request, pk):
    """A view for updating existing groups."""

    group = get_object_or_404(Group, pk=pk)
    user = request.user

    # Only creator who is in group can update the group.
    if user.id != group.creator.id or user not in group.users.all():
        return redirect(reverse('my_groups_view'))

    if request.method == 'POST':
        form = UpdateGroupForm(request.POST)
        if form.is_valid():
            group.name = form.cleaned_data['name']
            group.description = form.cleaned_data['description']
            group.last_edit_date = timezone.now()
            group.save()

            return redirect(reverse('group_view', args=(group.pk,)))

    form = UpdateGroupForm(instance=group)
    context = {
        'form': form,
    }

    return render(request, 'platformapp/update_group_view.html', context)


class DeleteGroupView(LoginRequiredMixin, DeleteView):
    """A view for deleting existing groups."""

    login_url = reverse_lazy('login_view')
    redirect_field_name = 'next'

    model = Group
    success_url = reverse_lazy('my_groups_view')
    template_name = 'platformapp/delete_group_view.html'

    def get(self, request, *args, **kwargs):
        """Redirect if request user is not in group or
        is not its creator."""

        group = self.get_object()
        user = request.user
        if user.id != group.creator.id or user not in group.users.all():
            return redirect('my_groups_view')

        return super().get(request, args, kwargs)

    def delete(self, request, *args, **kwargs):
        """Delete only if request user is its creator and
        is in the group."""

        group = self.get_object()
        user = request.user

        if user.id == group.creator.id and user in group.users.all():
            group.delete()

        return redirect(reverse('my_groups_view'))


@login_required
def group_view(request, pk):
    """Main view of group containing all tabs related to group
    and all tabs' elements."""

    group = get_object_or_404(Group, pk=pk)
    user = request.user

    if user not in group.users.all():
        return redirect(reverse('my_groups_view'))

    tabs = Tab.objects.filter(group_id=group.pk)
    tabs_dict = {tab: Element.objects.filter(tab_id=tab.pk) for tab in tabs}

    context = {
        'group': group,
        'tabs_dict': tabs_dict,
    }

    return render(request, 'platformapp/group_view.html', context)


@login_required
def my_groups_view(request):
    groups = request.user.joined_groups.all()
    context = {
        'groups': groups,
    }

    return render(request, 'platformapp/my_groups_view.html', context)


@login_required
def join_group_view(request, pk):
    """A view to join the group."""

    group = get_object_or_404(Group, pk=pk)

    if request.user in group.users.all():
        return redirect(reverse('my_groups_view'))

    if request.method == 'POST':
        group.users.add(request.user)
        return redirect(reverse('my_groups_view'))

    context = {
        'group': group,
    }

    return render(request, 'platformapp/join_group_view.html', context)


@login_required
def search_groups_view(request):
    """A view for searching groups."""

    context = {
        'search_result': []
    }

    if request.method == 'POST':
        query = request.POST['search_query']
        if query != '':
            search_result = Group.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(creator__username__icontains=query)
            )
            context['search_result'] = search_result

    return render(request, 'platformapp/search_groups_view.html', context)


@login_required
def leave_group_view(request, pk):
    """A view to leave the group."""

    group = get_object_or_404(Group, pk=pk)
    if request.user not in group.users.all():
        return redirect(reverse('my_groups_view'))

    if request.method == 'POST':
        group.users.remove(request.user)
        return redirect(reverse('my_groups_view'))

    context = {
        'group': group,
    }

    return render(request, 'platformapp/leave_group_view.html', context)

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import reverse, render, get_object_or_404, redirect
from django.urls import reverse_lazy

from ..models import Group
from ..forms import CreateGroupForm


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


class UpdateGroupView(UpdateView):
    pass


class DeleteGroupView(DeleteView):
    pass


def group_view(request, pk):
    pass


def my_groups_view(request):
    return render(request, 'platformapp/groups_view.html', {})


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


def search_groups_view(request):
    pass


def leave_group_view(request, pk):
    pass

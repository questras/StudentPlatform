from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse, render
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
    pass


def join_group_view(request):
    pass


def search_groups_view(request):
    pass


def leave_group_view(request, pk):
    pass

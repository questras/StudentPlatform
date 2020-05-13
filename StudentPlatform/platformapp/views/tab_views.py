from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseBadRequest
from django.shortcuts import reverse, redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required

from ..models import Group, Tab
from ..forms import CreateTabForm


@login_required
def create_tab_view(request, g_pk):
    """A view for creating new tabs."""

    group = get_object_or_404(Group, pk=g_pk)
    user = request.user

    if user not in group.users.all():
        return redirect(reverse('my_groups_view'))

    if request.method == 'POST':
        form = CreateTabForm(request.POST)
        if form.is_valid():
            tab = Tab(
                name=form.cleaned_data['name'],
                creator=user,
                group=group,
            )
            tab.save()
            return redirect(reverse('group_view', args=(group.pk,)))
        else:
            return HttpResponseBadRequest()

    form = CreateTabForm
    context = {
        'form': form,
    }

    return render(request, 'platformapp/create_tab_view.html', context)


class UpdateTabView(UpdateView):
    pass


class DeleteTabView(DeleteView):
    pass

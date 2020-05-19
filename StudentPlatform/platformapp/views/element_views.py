from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required

from ..models import Group, Tab, Element


class CreateElementView(CreateView):
    pass


class UpdateElementView(UpdateView):
    pass


class DeleteElementView(DeleteView):
    pass


@login_required
def element_view(request, g_pk, t_pk, pk):
    group = get_object_or_404(Group, pk=g_pk)
    tab = get_object_or_404(Tab, pk=t_pk)
    element = get_object_or_404(Element, pk=pk)

    if request.user not in group.users.all():
        return redirect(reverse('my_groups_view'))

    context = {
        'element': element,
    }

    return render(request, 'platformapp/element_view.html', context)

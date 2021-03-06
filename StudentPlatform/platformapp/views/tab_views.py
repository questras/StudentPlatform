from django.http import HttpResponseBadRequest
from django.shortcuts import reverse, redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

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

    return render(request, 'platformapp/tab/create_tab_view.html', context)


@login_required
def update_tab_view(request, pk):
    """A view for updating tabs."""

    tab = get_object_or_404(Tab, pk=pk)
    group = tab.group
    user = request.user

    if user not in group.users.all():
        return redirect(reverse('my_groups_view'))
    elif user.id != tab.creator.id:
        return redirect(reverse('group_view', args=(group.pk,)))

    if request.method == 'POST':
        form = CreateTabForm(request.POST)
        if form.is_valid():
            tab.name = form.cleaned_data['name']
            tab.last_edit_date = timezone.now()
            tab.save()
            return redirect(reverse('group_view', args=(group.pk,)))
        else:
            return HttpResponseBadRequest()

    form = CreateTabForm(instance=tab)
    context = {
        'form': form,
    }

    return render(request, 'platformapp/tab/update_tab_view.html', context)


@login_required
def delete_tab_view(request, pk):
    """A view for deleting tabs."""

    tab = get_object_or_404(Tab, pk=pk)
    group = tab.group
    user = request.user

    if user not in group.users.all():
        return redirect(reverse('my_groups_view'))
    elif user.id != tab.creator.id:
        return redirect(reverse('group_view', args=(group.pk,)))

    if request.method == 'POST':
        tab.delete()
        return redirect(reverse('group_view', args=(group.pk,)))

    return render(request, 'platformapp/tab/delete_tab_view.html', {})

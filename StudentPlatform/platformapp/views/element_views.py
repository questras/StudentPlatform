from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.contrib.auth import get_user_model

from ..forms import CreateElementForm
from ..models import Group, Tab, Element

User = get_user_model()


def create_element(form: CreateElementForm, user: User, tab: Tab) -> Element:
    """Create element with data from form, user as creator
    and tab as element's tab."""

    element = Element(
        name=form.cleaned_data['name'],
        text=form.cleaned_data['text'],
        image=form.cleaned_data['image'],
        creator=user,
        tab=tab
    )
    return element


def update_element(element: Element, form: CreateElementForm) -> Element:
    """Update element with data from form."""

    element.name = form.cleaned_data['name']
    element.text = form.cleaned_data['text']

    if form.cleaned_data['image'] is False:
        # "Clear" checkbox in form was selected.
        element.image = None

    if form.cleaned_data['image']:
        # New image was specified.
        element.image = form.cleaned_data['image']

    return element


@login_required
def create_element_view(request, g_pk, t_pk):
    """A view for creating new elements."""

    group = get_object_or_404(Group, pk=g_pk)
    tab = get_object_or_404(Tab, pk=t_pk)

    if request.user not in group.users.all():
        return redirect(reverse('my_groups_view'))

    if request.method == 'POST':
        form = CreateElementForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            element = create_element(form, request.user, tab)
            element.save()
            return redirect(reverse('element_view',
                                    args=(group.pk, tab.pk, element.pk)))
        else:
            return HttpResponseBadRequest()

    form = CreateElementForm
    context = {
        'form': form,
    }

    return render(request, 'platformapp/create_element_view.html', context)


@login_required
def update_element_view(request, g_pk, t_pk, pk):
    """A view for updating existing elements."""

    group = get_object_or_404(Group, pk=g_pk)
    tab = get_object_or_404(Tab, pk=t_pk)
    element = get_object_or_404(Element, pk=pk)
    user = request.user
    element_view_url = reverse('element_view',
                               args=(group.pk, tab.pk, element.pk,))

    if user not in group.users.all():
        return redirect(reverse('my_groups_view'))
    elif user.id != element.creator.id:
        return redirect(element_view_url)

    if request.method == 'POST':
        form = CreateElementForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            element = update_element(element, form)
            element.save()
            return redirect(element_view_url)
        else:
            return HttpResponseBadRequest()

    form = CreateElementForm(instance=element)
    context = {
        'form': form,
    }

    return render(request, 'platformapp/update_element_view.html', context)


@login_required
def delete_element_view(request, g_pk, t_pk, pk):
    """A view for deleting existing elements."""

    group = get_object_or_404(Group, pk=g_pk)
    tab = get_object_or_404(Tab, pk=t_pk)
    element = get_object_or_404(Element, pk=pk)
    user = request.user

    if user not in group.users.all():
        return redirect(reverse('my_groups_view'))
    elif user.id != element.creator.id:
        return redirect(reverse('element_view',
                                args=(group.pk, tab.pk, element.pk,)))

    if request.method == 'POST':
        element.delete()
        return redirect(reverse('group_view', args=(group.pk,)))

    return render(request, 'platformapp/delete_element_view.html')


@login_required
def element_view(request, g_pk, t_pk, pk):
    """Main view of an element."""

    group = get_object_or_404(Group, pk=g_pk)
    tab = get_object_or_404(Tab, pk=t_pk)
    element = get_object_or_404(Element, pk=pk)

    if request.user not in group.users.all():
        return redirect(reverse('my_groups_view'))

    context = {
        'group': group,
        'tab': tab,
        'element': element,
    }

    return render(request, 'platformapp/element_view.html', context)

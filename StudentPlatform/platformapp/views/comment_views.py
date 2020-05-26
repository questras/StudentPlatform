from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponseBadRequest

from ..models import Group, Element, Comment


@login_required
def add_comment_view(request, g_pk, t_pk, e_pk):
    """A view for creating new comments. Accepts only
    post requests."""

    group = get_object_or_404(Group, pk=g_pk)
    element = get_object_or_404(Element, pk=e_pk)
    element_view_url = reverse('element_view', args=(g_pk, t_pk, e_pk,))

    if request.user not in group.users.all():
        return redirect(reverse('my_groups_view'))

    if request.method == 'POST':
        if 'text' in request.POST.keys():
            comment = Comment(
                text=request.POST['text'],
                creator=request.user,
                element=element,
            )
            comment.save()
        else:
            return HttpResponseBadRequest()

    return redirect(element_view_url)


def delete_comment_view(request, g_pk, t_pk, e_pk, pk):
    """A view for deleting existing comments."""
    pass

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponseBadRequest

from ..forms import CreateCommentForm
from ..models import Element, Comment


@login_required
def add_comment_view(request, e_pk):
    """A view for creating new comments. Accepts only
    post requests."""

    element = get_object_or_404(Element, pk=e_pk)
    group = element.tab.group

    if request.user not in group.users.all():
        return redirect(reverse('my_groups_view'))

    if request.method == 'POST':
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                text=form.cleaned_data['text'],
                creator=request.user,
                element=element,
            )
            comment.save()
        else:
            return HttpResponseBadRequest()

    return redirect(reverse('element_view', args=(e_pk,)))


@login_required
def delete_comment_view(request, pk):
    """A view for deleting existing comments."""

    comment = get_object_or_404(Comment, pk=pk)
    group = comment.element.tab.group
    user = request.user
    element_view_url = reverse('element_view', args=(comment.element.pk,))

    if user not in group.users.all():
        return redirect(reverse('my_groups_view'))

    if user.id != comment.creator.id:
        return redirect(element_view_url)

    if request.method == 'POST':
        comment.delete()
        return redirect(element_view_url)

    return render(request, 'platformapp/comment/delete_comment_view.html')

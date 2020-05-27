from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required

from .. import scripts


def index_view(request):
    """Index page for unauthenticated users.

    Show index page for unauthenticated users and redirect
    to feed_view for authenticated users.
    """

    if request.user.is_authenticated:
        return redirect(reverse('feed_view'))

    return render(request, 'platformapp/index/index_view.html', {})


@login_required
def feed_view(request):
    """A view with list of actions made on groups, tabs,
    elements and comments related to user."""

    user = request.user

    groups = list(user.joined_groups.all())
    tabs = scripts.get_all_tabs_from_groups(groups)
    elements = scripts.get_all_elements_from_tabs(tabs)
    comments = scripts.get_all_comments_from_elements(elements)

    # Join all objects.
    entries = tabs + elements + comments
    # Sort all objects by descending date.
    entries = sorted(entries, key=lambda x: x.created_date, reverse=True)
    # Create pairs of object and its time.
    entries = [(entry, entry.__class__.__name__) for entry in entries]

    context = {
        'entries': entries,
    }

    return render(request, 'platformapp/index/feed_view.html', context)


def how_to_view(request):
    """A view with how-to instructions."""

    return render(request, 'platformapp/index/how_to_view.html', {})

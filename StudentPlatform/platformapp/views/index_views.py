from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required


def index_view(request):
    """Index page for unauthenticated users.

    Show index page for unauthenticated users and redirect
    to feed_view for authenticated users.
    """

    if request.user.is_authenticated:
        return redirect(reverse('feed_view'))

    return render(request, 'platformapp/index_view.html', {})


@login_required
def feed_view(request):
    """TODO: Implement feed_view"""

    return render(request, 'platformapp/feed_view.html', {})

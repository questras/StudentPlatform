from django.shortcuts import render, redirect, reverse


def index_view(request):
    """Index page for unauthenticated users.

    Show index page for unauthenticated users and redirect
    to feed_view for authenticated users.
    """

    if request.user.is_authenticated:
        return redirect(reverse('feed_view'))

    return render(request, 'platformapp/index_view.html', {})


def feed_view(request):
    pass

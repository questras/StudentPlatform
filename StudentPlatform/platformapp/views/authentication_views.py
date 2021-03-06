from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView
from django.contrib.auth import logout

from ..forms import RegistrationForm

LoginView = auth_views.LoginView


class SignUpView(CreateView):
    """A view to sign up new users."""

    form_class = RegistrationForm
    success_url = reverse_lazy('login_view')
    template_name = 'platformapp/authentication/signup_view.html'

    def get(self, request, *args, **kwargs):
        """Redirect to index if logged user tries to sign up."""

        if request.user.is_authenticated:
            return redirect(reverse_lazy('feed_view'))

        return super(SignUpView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Redirect to index if logged user tries to sign up."""

        if request.user.is_authenticated:
            return redirect(reverse_lazy('feed_view'))

        return super(SignUpView, self).post(request, *args, **kwargs)


def logout_view(request):
    """A view to logout."""

    if request.user.is_authenticated:
        logout(request)

    return redirect(reverse('index_view'))

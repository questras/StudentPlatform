from django.http import HttpResponseRedirect
from django.shortcuts import render
from platformapp.forms import RegistrationForm
from django.urls import reverse_lazy
from django.views import generic


def index(request):
    """Index view of the page."""
    try:
        _ = request.session['group']  # Check if there is group id in session
    except KeyError:
        request.session['group'] = -1  # Set group id as -1 (no group)

    return render(request, 'platformapp/index.html', {})


class SignUp(generic.CreateView):
    """A view to register an user"""
    form_class = RegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'platformapp/signup.html'

    def get(self, request, *args, **kwargs):
        """Redirect to index if logged user tries to sign up"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('index'))
        return super(SignUp, self).get(request, *args, **kwargs)

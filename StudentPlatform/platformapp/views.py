from django.http import HttpResponseRedirect
from django.shortcuts import render
from platformapp.forms import RegistrationForm, CreateGroupForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import Group


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


@login_required
def create_group(request):
    """A view to create a group"""
    # when user tries to create a group
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            creator = request.user
            share_url = 'placeholder.com'  # placeholder for now

            Group(name=name, description=description, creator=creator, share_url=share_url).save()
            return HttpResponseRedirect(reverse_lazy('index'))  # index as placeholder for now
    # when user opens view
    else:
        form = CreateGroupForm

    return render(request, 'platformapp/create_group.html', {'form': form})

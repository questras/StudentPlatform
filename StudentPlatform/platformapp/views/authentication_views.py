from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView

LoginView = auth_views.LoginView


class SignUpView(CreateView):
    pass


def logout_view(request):
    pass

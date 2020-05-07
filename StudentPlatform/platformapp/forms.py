from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Group, Tab

User = get_user_model()


class CreateGroupForm(forms.ModelForm):
    """Form for creating new groups"""

    class Meta:
        model = Group
        fields = ('name', 'description')


class CreateTabForm(forms.ModelForm):
    """Form for creating new tabs"""

    class Meta:
        model = Tab
        fields = ('name',)


class RegistrationForm(UserCreationForm):
    """Form for registering new users."""

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

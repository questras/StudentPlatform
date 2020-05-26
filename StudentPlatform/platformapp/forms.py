from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Group, Tab, Element

User = get_user_model()


class CreateGroupForm(forms.ModelForm):
    """Form for creating new groups"""

    class Meta:
        model = Group
        fields = ('name', 'description')


class UpdateGroupForm(forms.ModelForm):
    """Form for updating existing groups."""

    class Meta:
        model = Group
        fields = ('name', 'description')


class CreateTabForm(forms.ModelForm):
    """Form for creating new tabs"""

    class Meta:
        model = Tab
        fields = ('name',)


class CreateElementForm(forms.ModelForm):
    """Form for creating new elements."""

    class Meta:
        model = Element
        fields = ('name', 'text', 'image',)
        widgets = {
            'image': forms.FileInput(),
        }


class RegistrationForm(UserCreationForm):
    """Form for registering new users."""

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

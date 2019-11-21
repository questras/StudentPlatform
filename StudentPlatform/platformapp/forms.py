from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import Group, GroupUser

User = get_user_model()


class CreateGroupForm(forms.ModelForm):
    """Form for creating new groups"""

    class Meta:
        model = Group
        fields = ('name', 'description')


class RegistrationForm(UserCreationForm):
    """Form for registering new users"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        """Do not let already taken email be registered again"""
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError('the given email is already registered')
        return self.cleaned_data['email']

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

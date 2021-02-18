from django.forms import ModelForm, Textarea, FileInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Group, Tab, Element, Comment

User = get_user_model()


class CreateGroupForm(ModelForm):
    """Form for creating new groups"""

    class Meta:
        model = Group
        fields = ('name', 'description')


class UpdateGroupForm(ModelForm):
    """Form for updating existing groups."""

    class Meta:
        model = Group
        fields = ('name', 'description')


class CreateTabForm(ModelForm):
    """Form for creating new tabs"""

    class Meta:
        model = Tab
        fields = ('name',)


class CreateElementForm(ModelForm):
    """Form for creating new elements."""

    class Meta:
        model = Element
        fields = ('name', 'text', 'image',)
        widgets = {
            'image': FileInput(),
        }


class CreateCommentForm(ModelForm):
    """Form for creating new comments."""

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': '',
        }
        widgets = {
            'text': Textarea(attrs={'cols': 80, 'rows': 7}),
        }


class RegistrationForm(UserCreationForm):
    """Form for registering new users."""

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


class GroupUser(AbstractUser):
    """Custom user model"""
    pass


User = get_user_model()


class Group(models.Model):
    """Group model.

    Fields:
        name:           name of the group,
        description:    description of the group,
        creator:        user that created the group,
        users:          users in the group,
        created_date:   date when group was created,
        last_edit_date: date when group was edited the last time,
                        initially NULL.
    """
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=90)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='joined_groups')
    created_date = models.DateTimeField(auto_now_add=True)
    last_edit_date = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.pk}. Group "{self.name}" ' \
               f'created by "{self.creator.username}" ' \
               f'at {self.created_date}.'


class Tab(models.Model):
    """Tab model.

    Fields:
        name:           name of the tab,
        creator:        user that created the tab,
        group:          group that the tab belongs to,
        created_date:   date when tab was created,
        last_edit_date: date when tab was edited the last time,
                        initially NULL.
    """
    name = models.CharField(max_length=45)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    last_edit_date = models.DateTimeField(null=True)

    def __str__(self):
        return f'Group: "{self.group.name}" -> Tab: "{self.name}" ' \
               f'created by "{self.creator.username}" at {self.created_date}'


class Element(models.Model):
    """Element model.

    Fields:
        name:           name of the element,
        creator:        user that created the element,
        text:           text of the element,
        image:          image in element,
        tab:            tab that the element belongs to,
        created_date:   date when element was created,
        last_edit_date: date when element was edited the last time,
                        initially NULL.
    """
    name = models.CharField(max_length=45)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    last_edit_date = models.DateTimeField(null=True)

    def __str__(self):
        return f'Group: "{self.tab.group.name}" -> Tab: "{self.tab.name}" -> '\
               f'Element: "{self.name}" created by "{self.creator.username}" '\
               f'at {self.created_date}'

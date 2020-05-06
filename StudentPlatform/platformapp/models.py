from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


class GroupUser(AbstractUser):
    """Custom user model"""
    pass


User = get_user_model()


class Group(models.Model):
    """
    Group model.
    Fields:
        name:           name of the group,
        description:    description of the group,
        creator:        user that created the group,
        users:          users in the group,
        share_url:      url that enables to join the group.
    """
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=90)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='my_groups')
    share_url = models.URLField()

    def __str__(self):
        return '{} created by {}.'.format(self.name, self.creator.username)


class Tab(models.Model):
    """
    Tab model.
    Fields:
        name:       name of the tab,
        creator:    user that created the tab,
        group:      group that the tab belongs to.
    """
    name = models.CharField(max_length=45)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.group.name} -> {self.name} ' \
               f'created by {self.creator.username}'


class Element(models.Model):
    """
    Element model.
    Fields:
        name:       name of the element,
        creator:    user that created the element,
        text:       text of the element,
        image:      image in element,
        tab:        tab that the element belongs to.
    """
    name = models.CharField(max_length=45)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='images/')
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tab.group.name}->{self.tab.name}->{self.name} ' \
               f'created by {self.creator.username}'

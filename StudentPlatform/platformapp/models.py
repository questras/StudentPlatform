from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    """A model containing specification of a Group."""
    name = models.CharField(max_length=40)  # Name of the group
    description = models.CharField(max_length=90)  # Description of the group
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  # User that created the group
    share_url = models.URLField()  # Url to join the group

    def __str__(self):
        return "{} created by {}".format(self.name, self.creator.username)


class Tab(models.Model):
    """A model containing specification of a Tab in a Group."""
    name = models.CharField(max_length=45)  # Name of the tab
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  # User that created the tab
    group = models.ForeignKey(Group, on_delete=models.CASCADE)  # Group that holds the tab

    def __str__(self):
        return "{} -> {} created by {}".format(self.group.name, self.name, self.creator.username)


class Element(models.Model):
    """A model containing specification of an Element in a Tab."""
    name = models.CharField(max_length=45)  # Name of the element
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  # User that created the element
    text = models.TextField()  # Text area where user can write
    image = models.ImageField(upload_to='images/')  # An image added to the element by user
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE)  # Tab that holds the element

    def __str__(self):
        return "{}->{}->{} created by {}".format(
            self.tab.group.name,
            self.tab.name,
            self.name,
            self.creator.username
        )


class UserGroupRelation(models.Model):
    """
    A relation between user and group i.e which user
    belongs to which group
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User belonging to the group
    group = models.ForeignKey(Group, on_delete=models.CASCADE)  # Group to which the user belongs

    def __str__(self):
        return "{} belongs to {}".format(self.user.username, self.group.name)


class Comment(models.Model):
    """A model containing specification of comments in an element."""
    content = models.TextField()  # Text area where user can write comment text
    date = models.DateTimeField(auto_now_add=True)  # Auto added date of publishing of the comment
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  # User that added the comment
    element = models.ForeignKey(Element, on_delete=models.CASCADE)  # Element which is commented

    def __str__(self):
        return "{}->{}->{}->comment created by {}".format(
            self.element.tab.group.name,
            self.element.tab.name,
            self.element.name,
            self.creator.username
        )

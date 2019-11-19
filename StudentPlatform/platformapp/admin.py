from django.contrib import admin
from .models import Group, Tab, Element, UserGroupRelation, Comment

# Register your models here.
admin.site.register(Group)
admin.site.register(Tab)
admin.site.register(Element)
admin.site.register(UserGroupRelation)
admin.site.register(Comment)

from django.contrib import admin
from .models import Group, Tab, Element, GroupUser

admin.site.register(Group)
admin.site.register(Tab)
admin.site.register(Element)
admin.site.register(GroupUser)

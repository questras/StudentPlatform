from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', views.logout_view, name='logout_view'),
    path('create_group/', views.create_group, name='create_group'),
    path('create_tab/', views.create_tab, name='create_tab'),
    path('groups/', views.groups_view, name='groups_view'),
    path('groups/<int:group_id>/activate', views.activate_group, name='activate_group'),
    path('group_main/', views.group_main, name='group_main'),
]

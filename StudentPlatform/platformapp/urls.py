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
    path('search_group/', views.search_group, name='search_group'),
    path('<int:join_group_id>/join_group/', views.join_group_view, name='join_group_view'),
    path('<int:join_group_id>/join/', views.join_group, name='join_group'),
    path('<int:leaving_group_id>/leave/', views.leave_group, name='leave_group'),
    path('<int:deleting_tab_id>/delete_tab/', views.delete_tab, name='delete_tab'),

]

from django.urls import path

from .views.authentication_views import *
from .views.index_views import *
from .views.group_views import *
from .views.tab_views import *
from .views.element_views import *

urlpatterns = [
    # Index views:
    path('', index_view, name='index_view'),
    path('feed/', feed_view, name='feed_view'),
    # Authentication views:
    path('auth/signup/', SignUpView.as_view(), name='signup_view'),
    path('auth/login/', LoginView.as_view(), name='login_view'),
    path('auth/logout/', logout_view, name='logout_view'),
    # Group views:
    path('group/<int:pk>/', group_view, name='main_group_view'),
    path('group/<int:pk>/update/', UpdateView.as_view(), name='update_group_view'),
    path('group/<int:pk>/delete/', DeleteView.as_view(), name='delete_group_view'),
    path('group/<int:pk>/leave/', leave_group_view, name='leave_group_view'),
    path('create_group/', CreateGroupView.as_view(), name='create_group_view'),
    path('my_groups/', my_groups_view, name='my_groups_view'),
    path('join_group/<int:pk>/', join_group_view, name='join_group_view'),
    path('search_groups', search_groups_view, name='search_groups_view'),
    # Tab views:
    path('group/<int:g_pk>/create_tab/', CreateTabView.as_view(), name='create_tab_view'),
    path('group/<int:g_pk>/tab/<int:pk>/update/', UpdateTabView.as_view(), name='update_tab_view'),
    path('group/<int:g_pk>/tab/<int:pk>/delete/', DeleteTabView.as_view(), name='delete_tab_view'),
    # Element views:
    path('group/<int:g_pk>/tab/<int:t_pk>/create_element/', CreateElementView.as_view(), name='create_element_view'),
    path('group/<int:g_pk>/tab/<int:t_pk>/element/<int:pk>/', element_view, name='element_view'),
    path('group/<int:g_pk>/tab/<int:t_pk>/element/<int:pk>/update', UpdateElementView.as_view(),
         name='update_element_view'),
    path('group/<int:g_pk>/tab/<int:t_pk>/element/<int:pk>/delete', DeleteElementView.as_view(),
         name='delete_element_view'),
]

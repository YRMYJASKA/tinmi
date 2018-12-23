from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('a/login/', auth_views.LoginView.as_view(template_name='chat/login.html'), name='login'),
    path('a/logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('a/signup/', views.signup, name='signup'),
    path('c/', views.landing, name='landing'),
    path('c/create/', views.createroom, name='roomcreate'),
    path('c/<slug:slug>/', views.chatroom, name='chatroom'),
    path('c/leave/<slug:slug>/', views.leaveroom, name='leaveroom'),
    path('ajax/validate_room/', views.validate_room, name='validate_room'),
]

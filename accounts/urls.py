from django.urls import path
from . import views

# define account login, logout and register urls and views
urlpatterns = [
    path('login', views.account_login, name="login"),
    path('logout', views.account_logout, name="logout"),
    path('register', views.account_register, name="register"),
]

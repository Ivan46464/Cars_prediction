from django.urls import path
from cars_project.views.views import *

urlpatterns = [
    path('register', RegisterUser.as_view(), name='register'),
    path('login', LoginUser.as_view(), name='login'),
    path('logout', LogoutUser.as_view(), name='logout'),

    ]
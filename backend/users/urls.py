# backend/users/urls.py
from django.urls import path
from .views import RegisterView, UserView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("user/", UserView.as_view(), name="user"),
]

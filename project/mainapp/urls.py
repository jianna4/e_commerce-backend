from django.urls import path
from .views import register_view, login_view, me_view
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views

urlpatterns = [
    path('register/', register_view, name='register'),
    path("login/", login_view, name="login"),
    path("me/", me_view, name="me"),
   

]

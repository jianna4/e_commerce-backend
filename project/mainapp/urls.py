from django.urls import path
from .views import RegisterView ,me
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
      path('me/', views.me, name='me'),
   

]

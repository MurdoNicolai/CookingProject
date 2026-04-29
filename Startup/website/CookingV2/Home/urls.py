from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tailwind-test/', views.tailwind_test, name='tailwind_test'),
]

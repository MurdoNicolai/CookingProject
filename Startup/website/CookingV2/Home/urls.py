from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('1', views.home1, name='home1'),
    path('tailwind-test/', views.tailwind_test, name='tailwind_test'),
]

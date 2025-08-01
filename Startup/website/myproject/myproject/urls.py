"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from recipes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.recipe_search, name='recipe_search'),
    path('search/', views.search_recipes, name='search_recipes'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('recipe_buttons/', views.recipe_button_list, name='recipe_buttons'),
    path('recipe-display/', views.recipe_display, name='recipe-display'),
]

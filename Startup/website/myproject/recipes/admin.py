from django.contrib import admin
from .models import Recipe, Ingredient, Season, Geography

admin.site.register(Season)
admin.site.register(Geography)
admin.site.register(Recipe)
admin.site.register(Ingredient)


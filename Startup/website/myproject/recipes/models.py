from django.db import models

class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    folder_path = models.TextField()
    geography = models.TextField(null=True, blank=True)
    season = models.TextField(null=True, blank=True, default="all")
    ingredients = models.TextField()
    directions = models.TextField()
    cooking_time = models.TextField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    total_yield = models.TextField(null=True, blank=True)
    special_equipment = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('title', 'folder_path')
        db_table = 'recipes'

    def __str__(self):
        return self.title

class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = "ingredients"

class Season(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = "season"


class Geography(models.Model):
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    sub_region = models.CharField(max_length=255)
    intermediate_region = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = "geography"


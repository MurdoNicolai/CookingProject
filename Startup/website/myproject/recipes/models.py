from django.db import models

class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    folder_path = models.TextField()
    geography = models.TextField()
    season = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    cooking_time = models.IntegerField()
    difficulty = models.CharField(max_length=50, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')])

    def __str__(self):
        return self.title

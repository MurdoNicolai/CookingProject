# Generated by Django 5.1.3 on 2024-11-13 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('folder_path', models.TextField()),
                ('geography', models.TextField()),
                ('season', models.TextField()),
                ('ingredients', models.TextField()),
                ('instructions', models.TextField()),
                ('cooking_time', models.IntegerField()),
                ('difficulty', models.CharField(choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], max_length=50)),
            ],
        ),
    ]

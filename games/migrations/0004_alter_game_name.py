# Generated by Django 4.2.1 on 2023-06-12 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0003_alter_game_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="name",
            field=models.CharField(max_length=200),
        ),
    ]
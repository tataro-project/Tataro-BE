# Generated by Django 5.1.6 on 2025-02-19 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notice", "0005_delete_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notice",
            name="category",
            field=models.CharField(max_length=20),
        ),
    ]

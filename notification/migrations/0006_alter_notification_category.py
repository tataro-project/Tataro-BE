# Generated by Django 5.1.6 on 2025-02-23 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0005_remove_notiuser_read_users_notiuser_read_users"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="category",
            field=models.CharField(max_length=20),
        ),
    ]

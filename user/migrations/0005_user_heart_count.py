# Generated by Django 5.1.6 on 2025-02-24 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0004_alter_questionnaire_user_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="heart_count",
            field=models.IntegerField(default=0),
        ),
    ]

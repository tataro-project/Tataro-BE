# Generated by Django 5.1.6 on 2025-02-25 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tarot", "0004_remove_tarocardcontents_card_id_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tarocardcontents",
            options={"ordering": ["created_at"]},
        ),
        migrations.AlterModelOptions(
            name="tarochatcontents",
            options={"ordering": ["created_at"]},
        ),
        migrations.AlterModelOptions(
            name="tarochatrooms",
            options={"ordering": ["created_at"]},
        ),
    ]

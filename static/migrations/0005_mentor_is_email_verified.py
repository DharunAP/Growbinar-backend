# Generated by Django 4.2 on 2024-05-03 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('static', '0004_remove_mentor_is_email_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentor',
            name='is_email_verified',
            field=models.BooleanField(default=False),
        ),
    ]

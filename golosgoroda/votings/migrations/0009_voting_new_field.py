# Generated by Django 5.1.1 on 2024-10-07 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votings', '0008_alter_voting_completed_at_alter_voting_formed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='voting',
            name='new_field',
            field=models.IntegerField(default=0),
        ),
    ]

# Generated by Django 4.0.4 on 2022-04-28 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('album_bot', '0003_userstate_delete_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='user_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]

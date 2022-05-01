# Generated by Django 4.0.4 on 2022-05-01 11:51

import album_bot.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('album_bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to=album_bot.models.upload_directory_path),
        ),
        migrations.AlterField(
            model_name='userstate',
            name='state',
            field=models.CharField(choices=[('1', 'Initial'), ('2', 'Photo has been uploaded'), ('3', 'Creating new album')], default='1', max_length=2),
        ),
    ]
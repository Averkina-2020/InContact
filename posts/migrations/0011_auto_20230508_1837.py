# Generated by Django 2.2.6 on 2023-05-08 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20201021_0006'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='group',
        ),
        migrations.DeleteModel(
            name='Group',
        ),
    ]

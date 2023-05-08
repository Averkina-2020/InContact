# Generated by Django 2.2.6 on 2020-10-12 09:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20201005_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(
                blank=True,
                help_text='вы можете выбрать группу из списка',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='posts',
                to='posts.Group',
                verbose_name='Выберите группу'
                ),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(
                help_text='введите любой текст',
                verbose_name='Введите текст'
                ),
        ),
    ]

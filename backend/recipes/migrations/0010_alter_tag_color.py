# Generated by Django 3.2.16 on 2022-12-25 15:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20221225_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(regex='^#([A-Fa-f0-9]{6})$')], verbose_name='Цветовой HEX-код'),
        ),
    ]

# Generated by Django 3.2.16 on 2022-12-08 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20221208_1802'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
    ]
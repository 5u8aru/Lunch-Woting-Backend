# Generated by Django 5.2 on 2025-04-03 07:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_remove_menu_date_remove_menu_items_menu_day_of_week_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='menu',
            unique_together={('restaurant', 'day_of_week')},
        ),
    ]

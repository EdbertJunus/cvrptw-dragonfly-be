# Generated by Django 4.2 on 2023-04-28 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dragonApp', '0002_route_alter_store_latitude_alter_store_longitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='latitude',
            field=models.DecimalField(decimal_places=6, max_digits=10),
        ),
        migrations.AlterField(
            model_name='store',
            name='longitude',
            field=models.DecimalField(decimal_places=6, max_digits=10),
        ),
    ]

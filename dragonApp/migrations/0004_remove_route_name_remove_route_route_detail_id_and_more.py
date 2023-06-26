# Generated by Django 4.2 on 2023-05-09 03:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dragonApp', '0003_alter_store_latitude_alter_store_longitude'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='route',
            name='name',
        ),
        migrations.RemoveField(
            model_name='route',
            name='route_detail_id',
        ),
        migrations.AddField(
            model_name='routedetail',
            name='store_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='dragonApp.store'),
        ),
    ]

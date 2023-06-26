# Generated by Django 4.2 on 2023-04-28 16:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dragonApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('num_stores', models.IntegerField()),
                ('gasoline_price', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='store',
            name='latitude',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='store',
            name='longitude',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=10),
        ),
        migrations.CreateModel(
            name='RouteDetail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('store_name', models.CharField(max_length=200)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('demand', models.IntegerField()),
                ('tw_start', models.IntegerField()),
                ('tw_end', models.IntegerField()),
                ('route_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dragonApp.route')),
            ],
        ),
        migrations.AddField(
            model_name='route',
            name='route_detail_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dragonApp.routedetail'),
        ),
        migrations.AddField(
            model_name='route',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
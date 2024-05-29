# Generated by Django 5.0.6 on 2024-05-27 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Product Name')),
                ('price', models.FloatField()),
                ('pdetails', models.CharField(max_length=100, verbose_name='Product Details')),
                ('cat', models.IntegerField(choices=[(1, 'Mobile'), (2, 'Shoes'), (3, 'Clothes')], verbose_name='Category')),
                ('is_active', models.BooleanField(default=True, verbose_name='Available')),
            ],
        ),
    ]

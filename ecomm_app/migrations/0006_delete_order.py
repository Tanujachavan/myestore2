# Generated by Django 5.0.6 on 2024-05-27 10:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecomm_app', '0005_cart_qty_order'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Order',
        ),
    ]

# Generated by Django 3.1.1 on 2020-10-15 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_order_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='is_ready_for_shipping',
            new_name='is_delivered',
        ),
    ]
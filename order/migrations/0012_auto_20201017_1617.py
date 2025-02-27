# Generated by Django 3.1.1 on 2020-10-17 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_orderitem_date_delivered'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='is_return_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='is_return_requested',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='date_delivered',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

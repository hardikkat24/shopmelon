# Generated by Django 3.1.1 on 2020-10-17 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0010_orderitem_is_cancelled'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='date_delivered',
            field=models.DateTimeField(null=True),
        ),
    ]
# Generated by Django 3.1.1 on 2020-10-20 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_seller_gst_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='seller',
            name='amount_he_gets',
            field=models.IntegerField(default=0),
        ),
    ]

# Generated by Django 3.1.1 on 2020-10-16 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20201015_0630'),
    ]

    operations = [
        migrations.AddField(
            model_name='seller',
            name='amount_for_delivered',
            field=models.IntegerField(default=0),
        ),
    ]

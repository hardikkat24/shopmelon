# Generated by Django 3.1.1 on 2020-10-20 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_remove_customer_is_phone_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='seller',
            name='bank_account_bearers_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='seller',
            name='bank_branch_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='seller',
            name='bank_ifsc_code',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
        migrations.AddField(
            model_name='seller',
            name='upi_address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]

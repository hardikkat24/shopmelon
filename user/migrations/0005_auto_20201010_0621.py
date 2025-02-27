# Generated by Django 3.1.1 on 2020-10-10 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20200923_0747'),
    ]

    operations = [
        migrations.RenameField(
            model_name='seller',
            old_name='customer_contact_email',
            new_name='business_contact_email',
        ),
        migrations.RenameField(
            model_name='seller',
            old_name='customer_contact_phone',
            new_name='business_contact_phone',
        ),
        migrations.AlterField(
            model_name='seller',
            name='aadhar_no',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='seller',
            name='pan_no',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]

# Generated by Django 3.1.1 on 2020-10-20 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_auto_20201020_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='seller',
            name='gst_no',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='GST Number'),
        ),
    ]
# Generated by Django 3.1.1 on 2020-10-20 06:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_auto_20201020_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sub_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.subcategory'),
        ),
    ]
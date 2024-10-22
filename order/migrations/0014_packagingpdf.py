# Generated by Django 3.1.1 on 2020-10-20 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_auto_20201020_1819'),
        ('order', '0013_wishlistitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackagingPDF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf_url', models.URLField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.seller')),
            ],
        ),
    ]

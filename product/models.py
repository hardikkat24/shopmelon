from django.db import models
from PIL import Image

from user.models import Seller

VARIANT_TYPE_CHOICES = [
    ('C', 'Color'),
    ('S', 'Size')
]


class Category(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField()
    image = models.ImageField(upload_to='product/category/images/', default='default/category_image.jpg')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 800 or img.width > 800:
            output_size = (800, 800)
            img.thumbnail(output_size)
            img.save(self.image.path)

        return


class Product(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    description = models.TextField()
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    unit_price = models.IntegerField(null=False, blank=False)
    unit_mrp = models.IntegerField(null=False, blank=False)
    is_adult = models.BooleanField(default=False)
    style = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='product/product/images/', default='default/product_image.jpg')
    note = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 800 or img.width > 800:
            output_size = (800, 800)
            img.thumbnail(output_size)
            img.save(self.image.path)

        return


class Variant(models.Model):
    type = models.CharField(max_length=1, choices=VARIANT_TYPE_CHOICES, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    quantity_available = models.IntegerField(null=False, blank=False)
    image = models.ImageField(upload_to='product/variant/images/', null=True, blank=True)

    def is_available(self):
        return self.quantity_available > 0

    def __str__(self):
        return self.type.verbose_name + self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 800 or img.width > 800:
            output_size = (800, 800)
            img.thumbnail(output_size)
            img.save(self.image.path)

        return

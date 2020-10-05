from django.db import models
from PIL import Image

from user.models import Seller

VARIANT_TYPE_CHOICES = [
    ('C', 'Color'),
    ('S', 'Size'),
    ('U', 'Units')
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
    has_variants = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', null=True, blank=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return self.name

    @property
    def discount_price(self):
        return self.unit_mrp - self.unit_price

    @property
    def discount_percent(self):
        return (self.unit_mrp - self.unit_price)/self.unit_mrp*100

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.variant_set.count() > 1:
            self.has_variants = True
            super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 800 or img.width > 800:
            output_size = (800, 800)
            img.thumbnail(output_size)
            img.save(self.image.path)

        return


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=VARIANT_TYPE_CHOICES, null=False, blank=True, default='')
    name = models.CharField(max_length=100, null=False, blank=True, default='')
    quantity_available = models.IntegerField(null=False, blank=False)
    image = models.ImageField(upload_to='product/variant/images/', null=True, blank=True)

    def is_available(self):
        return self.quantity_available > 0

    def __str__(self):
        return self.type + self.name + str(self.product)

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def can_order(self, quantity):
        return self.quantity_available >= quantity

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.image.path)

            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.image.path)
        except:
            pass

        return


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
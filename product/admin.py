from django.contrib import admin

from .models import Category, Product, Variant, Tag, ProductImage, SubCategory

admin.site.register([Category, Product, Variant, Tag, ProductImage, SubCategory])

from django.contrib import admin

from .models import Category, Product, Variant, Tag

admin.site.register([Category, Product, Variant, Tag])

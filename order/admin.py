from django.contrib import admin

from order.models import Order, OrderItem, WishlistItem

admin.site.register([Order, OrderItem, WishlistItem])

from django.contrib import admin

from order.models import Order, OrderItem, Payment

admin.site.register([Order, OrderItem, Payment])

from django.contrib import admin
from .models import CustomUser, Customer, Seller, Address

admin.site.register([CustomUser, Customer, Seller, Address])

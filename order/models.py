from django.db import models

from user.models import Customer
from product.models import Product, Variant

PAYMENT_TYPE_CHOICES = [
    ('C', 'Cash on Delivery'),
    ('N', 'Net Banking'),
    ('D', 'Debit/Credit Card')
]

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_ordered = models.DateTimeField(null=True, blank=True)
    date_shipped = models.DateTimeField(null=True, blank=True)
    is_order_placed = models.BooleanField(default=False)
    is_payment_done = models.BooleanField(default=False)
    is_ready_for_shipping = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk) + self.customer


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=PAYMENT_TYPE_CHOICES, null=False, blank=False)
    amount = models.IntegerField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)


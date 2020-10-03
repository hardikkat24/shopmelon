from django.db import models

from user.models import Customer
from product.models import Product, Variant

PAYMENT_TYPE_CHOICES = [
    ('C', 'Cash on Delivery'),
    ('N', 'Net Banking'),
    ('D', 'Debit/Credit Card')
]

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_ordered = models.DateTimeField(null=True, blank=True)
    date_shipped = models.DateTimeField(null=True, blank=True)
    is_order_placed = models.BooleanField(default=False)
    is_payment_done = models.BooleanField(default=False)
    is_ready_for_shipping = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)

    def get_total_amount_and_quantity(self):
        quantity = amount = 0
        order_items = self.orderitem_set.all().prefetch_related('variant', 'variant__product')
        for order_item in order_items:
            quantity = quantity + order_item.quantity
            amount = amount + order_item.quantity*order_item.variant.product.unit_price

        return (amount, quantity)

    def __str__(self):
        return str(self.pk) + str(self.customer)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    @property
    def total_amount(self):
        return self.quantity * self.variant.product.unit_price


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=PAYMENT_TYPE_CHOICES, null=False, blank=False)
    amount = models.IntegerField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)


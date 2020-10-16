from django.db import models

from user.models import Customer, Address
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
    is_cancelled = models.BooleanField(default=False)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    invoice_url = models.URLField(null=True, blank=True)

    def get_total_amount_and_quantity(self):
        quantity = amount = 0
        order_items = self.orderitem_set.all().prefetch_related('variant', 'variant__product')
        for order_item in order_items:
            quantity = quantity + order_item.quantity
            amount = amount + order_item.quantity*order_item.variant.product.unit_price

        return (amount, quantity)

    def __str__(self):
        return str(self.pk) + str(self.customer)

    @property
    def status(self):
        if self.is_cancelled:
            return ('C', 'Cancelled')

        order_items = self.orderitem_set.all()
        count = 0
        partial = False
        for order_item in order_items:
            if order_item.is_delivered:
                count = count + 1
            else:
                partial = True
        if count == 0:
            return ('P', 'Order Placed')
        if partial:
            return ('N', 'Partially Delivered')

        return ('D', 'Delivered')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    is_shipped = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)

    @property
    def total_amount(self):
        return self.quantity * self.variant.product.unit_price

    @property
    def status(self):
        if self.is_delivered:
            return ('D', 'Delivered')
        if self.is_shipped:
            return ('S', 'Shipped')
        return ('N', 'Not Shipped')

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            self.delete()
        else:
            super().save(*args, **kwargs)
        return

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=PAYMENT_TYPE_CHOICES, null=False, blank=False)
    amount = models.IntegerField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)


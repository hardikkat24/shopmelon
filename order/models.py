from django.db import models
from django.utils import timezone
from django.conf import settings

from user.models import Customer, Address, Seller
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
    is_cancelled = models.BooleanField(default=False)
    date_delivered = models.DateTimeField(null=True, blank=True)
    is_return_requested = models.BooleanField(default=False)
    is_return_completed = models.BooleanField(default=False)
    @property
    def total_amount(self):
        return self.quantity * self.variant.product.unit_price

    @property
    def status(self):
        if self.is_return_completed:
            return ('R', 'Returned')
        if self.is_return_requested:
            return ('RR', 'Return Requested')
        if self.is_cancelled:
            return ('C', 'Cancelled')
        if self.is_delivered:
            return ('D', 'Delivered')
        if self.is_shipped:
            return ('S', 'Shipped')
        return ('N', 'Not Shipped')

    @property
    def can_return(self):
        try:
            if self.variant.product.is_returnable:
                delta = timezone.localtime(timezone.now()).date() - self.date_delivered.date()

                if delta.days <= settings.MAX_DAYS_BEFORE_RETURN:
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False


    def cancel_or_notify(self):
        if self.is_delivered is False:
            self.is_cancelled = True
            self.save()
            # self.variant.product.seller.undelivered(self.total_amount)
            return True
        else:
            return False

    def return_item(self):
        self.is_return_requested = True
        self.save()
        return

    def return_item_complete(self):
        self.is_return_completed = True
        self.save()
        self.variant.product.seller.undelivered(self.total_amount)
        return

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


class WishlistItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)


class PackagingPDF(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    pdf_url = models.URLField(null=True, blank=True)
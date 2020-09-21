from django.db import models
from django.contrib.auth.models import AbstractUser

from PIL import Image

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(max_length=255, unique=True)
    image = models.ImageField(upload_to='user/customuser/images/', default='default/user_image.jpg')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 400 or img.width > 400:
            output_size = (400, 400)
            img.thumbnail(output_size)
            img.save(self.image.path)

        return 


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, null=False, blank=False)
    is_phone_verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class Seller(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200, null=False, blank=False)
    phone = models.CharField(max_length=10, null=False, blank=False)
    customer_contact_phone = models.CharField(max_length=10, null=True, blank=True)
    customer_contact_email = models.EmailField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.business_name) + ": " + str(self.user)


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    line1 = models.CharField(max_length=255, null=False, blank=False)
    line2 = models.CharField(max_length=255, null=False, blank=False)
    city = models.CharField(max_length=100, null=False, blank=False)
    state = models.CharField(max_length=100, null=False, blank=False)
    pincode = models.CharField(max_length=6, null=False, blank=False)

    def __str__(self):
        return str(self.user) + self.pk

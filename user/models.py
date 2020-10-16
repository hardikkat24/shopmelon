from django.db import models
from django.contrib.auth.models import AbstractUser

from PIL import Image

class CustomUser(AbstractUser):
    email = models.EmailField(max_length=255, unique=True)
    image = models.ImageField(upload_to='user/customuser/images/', default='default/user_image.jpg', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

    def save(self, *args, **kwargs):
        self.username = self.email
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
    business_contact_phone = models.CharField(max_length=10, null=True, blank=True)
    business_contact_email = models.EmailField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    aadhar_no = models.CharField(max_length=12, null=True, blank=True)
    pan_no = models.CharField(max_length=10, null=True, blank=True)
    amount_for_delivered = models.IntegerField(default=0)

    def __str__(self):
        return str(self.business_name) + ": " + str(self.user)

    def delivered(self, amount):
        self.amount_for_delivered = self.amount_for_delivered + amount
        self.save()

    def undelivered(self, amount):
        self.amount_for_delivered = self.amount_for_delivered - amount
        self.save()


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    line1 = models.CharField(max_length=255, null=False, blank=True)
    line2 = models.CharField(max_length=255, null=False, blank=True)
    city = models.CharField(max_length=100, null=False, blank=True)
    state = models.CharField(max_length=100, null=False, blank=True)
    pincode = models.CharField(max_length=6, null=False, blank=True)

    def __str__(self):
        return str(self.user) + str(self.pk)

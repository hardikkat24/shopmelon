from django import forms
from django.contrib.auth.forms import UserCreationForm
from user.models import CustomUser, Customer, Seller


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'image')


class CustomerCreationForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ('is_phone_verified', 'user')


class SellerCreationForm(forms.ModelForm):
    class Meta:
        model = Seller
        exclude = ('is_verified', 'user')
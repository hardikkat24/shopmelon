from django import forms
from django.contrib.auth.forms import UserCreationForm
from user.models import CustomUser, Customer, Seller


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'image')

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'image')
        exclude = ('password', 'password2')

class CustomerCreationForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ('is_phone_verified', 'user')


class SellerCreationForm1(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ('business_name', 'phone',)


class SellerCreationForm2(forms.ModelForm):
    class Meta:
        model = Seller
        exclude = ('user', 'is_verified',)



class EmailResendForm(forms.Form):
    email = forms.EmailField(required=True)
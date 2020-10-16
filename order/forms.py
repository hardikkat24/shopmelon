from django import forms
from user.models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ( 'line1', 'line2', 'city', 'state', 'pincode',)
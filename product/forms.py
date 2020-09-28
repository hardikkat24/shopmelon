from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from .models import Product, Variant


class ProductCreationForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('seller', 'tags')


class VariantCreationForm(forms.ModelForm):
    class Meta:
        model = Variant
        exclude = ('product', )


class TagCreationForm(forms.Form):
    tags = forms.CharField(widget=forms.Textarea, label='Tags', required=False)
    class Meta:
        fields = ('tags')


VariantFormset = modelformset_factory(
    Variant,
    fields=('type', 'name', 'quantity_available', 'image',),
    extra = 1,
)

VariantFormsetUpdate = modelformset_factory(
    Variant,
    fields=('type', 'name', 'quantity_available', 'image', 'id'),
    extra = 0,
)
from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from .models import Product, Variant, Category


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
    fields=('type', 'name', 'quantity_available', 'image'),
    extra = 1,
)

class ProductFilterForm(forms.Form):
    text = forms.CharField(required=False)
    category = forms.ChoiceField(choices=[(0,'-----')]+list(Category.objects.values_list('id','name')), required=False)
    price_gt = forms.DecimalField(label = 'Price from: ', required=False)
    price_lt = forms.DecimalField(label = 'Price to: ', required=False)


VariantNewFormset = inlineformset_factory(Product, Variant, fields=('type', 'name', 'quantity_available', 'image'), can_delete=False, extra=5)
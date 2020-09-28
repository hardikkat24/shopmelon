from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from product.models import Product, Variant, Tag
from .forms import ProductCreationForm, VariantFormset, VariantFormsetUpdate, TagCreationForm


@login_required
def add_product(request):
    user = request.user

    # only verified sellers can add products
    if not hasattr(user, 'seller') or not user.seller.is_verified:
        messages.info(request, 'You must be a verified seller to add products!')
        return redirect('home')

    if request.method == 'POST':
        form = ProductCreationForm(request.POST, request.FILES)
        formset = VariantFormset(request.POST, request.FILES)

        if formset.is_valid() and form.is_valid():
            # tags = form.cleaned_data['tag_s']
            # print(tags)
            product = form.save(commit=False)
            product.seller = user.seller
            product.save()

            if product.has_variants:
                # has_variants => multiple saved
                for variant_form in formset:
                    variant = variant_form.save(commit=False)
                    variant.product = product
                    variant.save()

            else:
                variant = formset[0].save(commit=False)
                variant.product = product
                variant.save()

            return redirect('tags', product.pk)

    else:
        form = ProductCreationForm()
        qs = Variant.objects.none()
        formset = VariantFormset(queryset=qs)

    context = {
        'form': form,
        'formset': formset,
    }

    return render(request, 'product/add_product.html', context)


@login_required
def update_product(request, pk):
    user = request.user
    try:
        product = Product.objects.get(pk=pk)
    except:
        return HttpResponseNotFound('Page not found')
    if not (hasattr(user, 'seller') and product.seller == user.seller):
        return HttpResponseNotAllowed('You are not allowed to view this page.')

    if request.method == 'POST':
        form = ProductCreationForm(request.POST, request.FILES, instance = product)
        formset = VariantFormsetUpdate(request.POST, request.FILES)

        if formset.is_valid() and form.is_valid():
            # tags = form.cleaned_data['tag_s']
            # print(tags)

            product_new = form.save(commit=False)
            if len(formset) > 1:
                product.has_variants = True
            product_new.save()

            if product_new.has_variants:
                # has_variants => multiple saved
                for variant_form in formset:
                    variant = variant_form.save(commit=False)
                    variant.product = product
                    variant.save()

            else:
                variant = formset[0].save(commit=False)
                variant.product = product
                variant.save()

            return redirect('home')
    else:
        form = ProductCreationForm(instance=product)
        qs = product.variant_set.all()
        formset = VariantFormsetUpdate(queryset=qs)

    context = {
        'form': form,
        'formset': formset,
    }

    return render(request, 'product/update_product.html', context)


def products(request):
    products = Product.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 20)

    try:
        paginated_products = paginator.page(page)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)

    context = {
        'products': paginated_products,
    }
    return render(request, 'product/products.html', context)


def product_description(request, pk):
    user = request.user
    has_update_permission = True
    try:
        product = Product.objects.get(pk=pk)
    except:
        return HttpResponseNotFound('Page not found')

    if not (hasattr(user, 'seller') and product.seller == user.seller):
        has_update_permission = False

    context = {
        'has_update_permission': has_update_permission,
        'tags': product.tags.all(),
        'variants': product.variant_set.all(),
        'product': product,
    }

    return render(request, 'product/product_description.html', context)


@login_required
def manage_products(request):
    user = request.user
    seller = user.seller
    if not hasattr(user, 'seller'):
        return HttpResponseNotAllowed('You are not allowed to view this page.')

    products = seller.product_set.all()

    context = {
        'products': products
    }

    return render(request, 'product/manage_products.html', context)


@csrf_exempt
def ajax_delete_variant(request):
    data = request.POST.get('id', None)
    id = json.loads(data)

    print(id)
    try:
        variant = Variant.objects.get(pk=id)
        variant.delete()
        message = 'Success'
    except:
        message = 'Failure'

    response = {
        'message': message
    }
    return JsonResponse(response)

@login_required
def tags(request, pk):
    user = request.user
    try:
        product = Product.objects.get(pk=pk)
    except:
        return HttpResponseNotFound('Page not found')

    if not (hasattr(user, 'seller') and product.seller == user.seller):
        return HttpResponseNotAllowed('You are not allowed to view this page.')



    if request.method == 'POST':
        form = TagCreationForm(request.POST)
        if form.is_valid():
            tags = [x.strip() for x in form.cleaned_data['tags'].split(',')]
            objList = []
            for tag in tags:
                objList.append(Tag.objects.get_or_create(name=tag)[0])
            product.tags.add(*objList)
    else:
        form = TagCreationForm()


    tags_to_be_passed = product.tags.all()
    context = {
        'form': form,
        'tags': tags_to_be_passed,
        'product': product
    }

    return render(request, 'product/tags.html', context)


@csrf_exempt
def ajax_delete_tags(request):
    tags = request.POST.get('tags', None)
    product_id = request.POST.get('product_id', None)
    tags = json.loads(tags)

    list = [int(x) for x in tags]
    print(list)

    tags_to_be_removed = Tag.objects.filter(pk__in=list)
    product = Product.objects.get(pk=product_id)

    product.tags.remove(*tags_to_be_removed)
    return JsonResponse({'message': 'yes'})
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from product.models import Product, Variant, Tag, Category, ProductImage
from .forms import ProductCreationForm, VariantFormset, VariantFormsetUpdate, TagCreationForm, ProductFilterForm, VariantNewFormset


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

            for file in request.FILES.getlist('images'):
                instance = ProductImage(
                    product=product,
                    image=file
                )
                instance.save()

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
        variants = product.variant_set.all()
    except:
        return HttpResponseNotFound('Page not found')
    if not (hasattr(user, 'seller') and product.seller == user.seller):
        return HttpResponseNotAllowed('You are not allowed to view this page.')

    if request.method == 'POST':
        form = ProductCreationForm(request.POST, request.FILES, instance = product)

        if form.is_valid():
            product_new = form.save(commit=False)
            product_new.save()
            return redirect('product-description', product.pk)
    else:
        form = ProductCreationForm(instance=product)

    print(variants)
    context = {
        'product': product,
        'form': form,
        'variants': variants,
    }

    return render(request, 'product/update_product.html', context)


@login_required
def manage_variants(request, pk):
    user = request.user
    try:
        product = Product.objects.get(pk=pk)
        variants = product.variant_set.all()
    except:
        return HttpResponseNotFound('Page not found')
    if not (hasattr(user, 'seller') and product.seller == user.seller):
        return HttpResponseNotAllowed('You are not allowed to view this page.')


    if request.method == 'POST':
        # updating existing variants quantities available
        for key in request.POST.keys():
            if key.isnumeric():
                variant = Variant.objects.get(pk=key)
                qty = int(request.POST.get(key))
                if qty <= 0:
                    variant.delete()
                else:
                    variant.quantity_available = qty
                    variant.save()

        formset = VariantNewFormset(request.POST, request.FILES, instance = product)
        if formset.is_valid():
            formset.save()
            formset = VariantNewFormset()

        product.save()

    else:
        formset = VariantNewFormset()
    context = {
        'product': product,
        'variants': variants,
        'formset': formset,
    }

    return render(request, 'product/manage_variants.html', context)


@login_required
def manage_images(request, pk):
    user = request.user
    try:
        product = Product.objects.get(pk=pk)
        images = product.productimage_set.all()
    except:
        return HttpResponseNotFound('Page not found')
    if not (hasattr(user, 'seller') and product.seller == user.seller):
        return HttpResponseNotAllowed('You are not allowed to view this page.')

    if request.method == 'POST':
        for file in request.FILES.getlist('images'):
            instance = ProductImage(
                product=product,
                image=file
            )
            instance.save()

    context = {
        'product': product,
        'images': images
    }

    return render(request, 'product/manage_images.html', context)


@login_required
@csrf_exempt
def ajax_delete_image(request):
    data = request.POST.get('id', None)
    id = json.loads(data)

    try:
        product_image = ProductImage.objects.get(pk=id)
        product_image.delete()
        message = 'Success'
    except:
        message = 'Failure'

    response = {
        'message': message
    }
    return JsonResponse(response)


@login_required
def delete_product(request, pk):
    user = request.user
    try:
        product = Product.objects.get(pk=pk)
    except:
        return HttpResponseNotFound('Page not found')
    if not (hasattr(user, 'seller') and product.seller == user.seller):
        return HttpResponseNotAllowed('You are not allowed to view this page.')

    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('manage-products')


def search(request):
    form = ProductFilterForm(request.GET)

    if form.is_valid():
        text = form.cleaned_data['text']
        category_pk = form.cleaned_data['category']
        price_gt = form.cleaned_data['price_gt']
        price_lt = form.cleaned_data['price_lt']

        # text handling
        if text.strip() != '':
            list = [x.strip().lower() for x in text.split(' ')]
            tags = Tag.objects.filter(name__in=list)
            products = Product.objects.none()
            for tag in tags:
                products = products | tag.product_set.all()
            products = products.distinct()
        else:
            products = Product.objects.all()

        # category handling
        if category_pk != '0' and category_pk != '':
            category = Category.objects.get(pk=category_pk)
            products = products.filter(category=category)

        if (price_lt is not None and price_lt is not None):
            products = products.filter(unit_price__gte=price_gt, unit_price__lte=price_lt)
        elif price_lt is not None:
            products = products.filter(unit_price__lte=price_lt)
        elif price_gt is not None:
            products = products.filter(unit_price__gte=price_gt)
    else:
        products = Product.objects.all()

    products = products.distinct()
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 10)

    try:
        paginated_products = paginator.page(page)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)

    context = {
        'products': paginated_products,
        'form': form,
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
        return HttpResponseNotAllowed('You are not allowed to view this.')

    context = {
        'tags': product.tags.all(),
        'variants': product.variant_set.all(),
        'product': product,
        'images': product.productimage_set.all(),
    }
    print(product.productimage_set.count())
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

    try:
        variant = Variant.objects.get(pk=id)
        variant.delete()
        variant.product.save()
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
                if tag != '':
                    objList.append(Tag.objects.get_or_create(name=tag.lower())[0])
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
    tag = request.POST.get('tag', None)
    product_id = request.POST.get('product_id', None)



    tag_to_be_removed = Tag.objects.get(pk=int(tag))
    product = Product.objects.get(pk=product_id)

    product.tags.remove(tag_to_be_removed)
    return JsonResponse({'message': 'yes'})
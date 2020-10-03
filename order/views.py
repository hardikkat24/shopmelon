from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from product.models import Variant
from order.models import Order, OrderItem


@csrf_exempt
def ajax_add_to_cart(request):
    user = request.user

    quantity = request.POST.get('quantity')
    if quantity == '':
        quantity = 1
    quantity = int(quantity)
    variant_pk = request.POST.get('variant_pk', None)

    if variant_pk is None:
        return JsonResponse({'message': 'Please select a variant.', 'type': 'info'})

    try:
        variant = Variant.objects.get(pk=variant_pk)
    except:
        return JsonResponse({'message': 'Invalid variant.', 'type': 'info'})

    # check stock availability
    if not variant.can_order(quantity):
        return JsonResponse({'message': 'Only '+ str(variant.quantity_available) + ' pieces left.', 'type': 'info'})

    if user.is_authenticated:
        order, _ = Order.objects.get_or_create(customer=user.customer, is_order_placed=False)
    else:
        cart = request.POST.get('cart')
        if cart == '0': # no cart created previously
            order = Order.objects.create()
            created_cart = True
        else:
            order = Order.objects.get(pk=cart)
            created_cart = False
    order_item, _ = OrderItem.objects.get_or_create(order = order, variant=variant)
    order_item.quantity = quantity
    order_item.save()

    return JsonResponse({'message': 'Item successfully added to cart', 'type': 'success', 'created_cart': created_cart, 'cart': order.pk})


def cart(request):
    user = request.user

    try:
        if user.is_authenticated:
            order = Order.objects.get(customer=user.customer, is_order_placed=False)
        else:
            order = Order.objects.get(pk = request.COOKIES.get('cart'))
        order_items = order.orderitem_set.all()
        amount, quantity = order.get_total_amount_and_quantity()
        context = {
            'cart_is_empty': False,
            'order': order,
            'order_items': order_items,
            'amount': amount,
            'quantity': quantity,
        }

    except:
        context = {
            'cart_is_empty': True,
        }

    return render(request, 'order/cart.html', context)


@csrf_exempt
@login_required
def ajax_delete_from_cart(request):
    user = request.user

    order_item_pk = request.POST.get('order_item_pk', 0)
    if order_item_pk == '':
        return JsonResponse({'message': 'Invalid data.', 'type': 'danger'})

    try:
        order_item = OrderItem.objects.get(pk=order_item_pk)
    except:
        return JsonResponse({'message': 'No such item in cart.', 'type': 'info'})

    if not order_item.order.customer == user.customer:
        return JsonResponse({'message': 'Invalid request', 'type': 'danger'})

    order = order_item.order
    order_item.delete()

    amount, quantity = order.get_total_amount_and_quantity()
    return JsonResponse({'message': 'Item successfully removed from cart', 'type': 'success', 'change': True, 'quantity':quantity, 'amount': amount})


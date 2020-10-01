from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from product.models import Variant
from order.models import Order, OrderItem


@csrf_exempt
@login_required
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

    order, _ = Order.objects.get_or_create(customer=user.customer, is_order_placed=False)
    order_item, _ = OrderItem.objects.get_or_create(order = order, variant=variant)
    order_item.quantity = quantity
    order_item.save()

    return JsonResponse({'message': 'Item successfully added to cart', 'type': 'success'})


def cart(request):
    user = request.user

    try:
        order = Order.objects.get(customer=user.customer, is_order_placed=False)
        print(order)
        order_items = order.orderitem_set.all()
        print(order_items)
        amount, quantity = order.get_total_amount_and_quantity()
        print(amount, quantity)
        context = {
            'cart_is_empty': False,
            'order': order,
            'order_items': order_items,
            'amount': amount,
            'quantity': quantity,
        }

    except:
        print('here')
        context = {
            'cart_is_empty': True,
        }

    return render(request, 'order/cart.html', context)
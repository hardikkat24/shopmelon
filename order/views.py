from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
import os
import razorpay
from datetime import datetime
from django.conf import settings
from django.utils import timezone

from user.models import Address
from product.models import Variant
from order.models import Order, OrderItem, WishlistItem, PackagingPDF
from .forms import AddressForm
from.utils import checkOrder, finaliseOrder

RP_KEY_ID = os.environ.get('RP_KEY_ID')
RP_KEY_SECRET = os.environ.get('RP_KEY_SECRET')
client = razorpay.Client(auth=(RP_KEY_ID, RP_KEY_SECRET))

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
        else:
            try:
                order = Order.objects.get(pk=cart)
            except:
                order = Order.objects.create()
    order_item, _ = OrderItem.objects.get_or_create(order = order, variant=variant)
    order_item.quantity = quantity
    order_item.save()

    return JsonResponse({'message': 'Item successfully added to cart', 'type': 'success', 'cart': order.pk})


def cart(request):
    user = request.user

    try:
        if user.is_authenticated:
            order = Order.objects.get(customer=user.customer, is_order_placed=False)
        else:
            order = Order.objects.get(pk = request.COOKIES.get('cart'))
        order_items = order.orderitem_set.all()
        if len(order_items) == 0:
            raise Exception("Sorry, no numbers below zero")
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
def ajax_delete_from_cart(request):
    user = request.user

    order_item_pk = request.POST.get('order_item_pk', 0)
    if order_item_pk == '':
        return JsonResponse({'message': 'Invalid data.', 'type': 'danger'})

    try:
        order_item = OrderItem.objects.get(pk=order_item_pk)
    except:
        return JsonResponse({'message': 'No such item in cart.', 'type': 'info'})

    order = order_item.order
    if user.is_authenticated:
        if not order_item.order.customer == user.customer:
            return JsonResponse({'message': 'Invalid request', 'type': 'danger'})
    else:
        if not(order.customer == None and order.pk == int(request.COOKIES.get('cart'))):
            return JsonResponse({'message': 'Invalid request', 'type': 'danger'})


    order_item.delete()

    amount, quantity = order.get_total_amount_and_quantity()
    return JsonResponse({'message': 'Item successfully removed from cart', 'type': 'success', 'change': True, 'quantity':quantity, 'amount': amount})


@login_required
def place_order(request):
    user = request.user
    address_existing = user.address_set.all()
    form = AddressForm()

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address_id = request.POST.get('cb', None)
            create_new_address = (address_id=='0')

            if create_new_address:
                print('save')
                address = form.save(commit=False)
                if address.line1=='' or address.city=='' or address.state=='' or address.pincode=='':
                    form.add_error(None, 'Enter valid address')
                else:
                    address.user = user
                    address.save()
                    address_id = address.pk
                    print('redirect')
                    return redirect('create-order', address_id)

            else:
                return redirect('create-order', address_id)

    context = {
        'form': form,
        'addresses': address_existing,
    }
    return render(request, 'order/place_order.html', context)


@login_required
def create_order(request, pk):
    user = request.user

    try:
        order = Order.objects.get(customer=user.customer, is_order_placed=False)
    except:
        messages.info(request, 'No item in cart.')
        redirect('cart')

    try:
        address = Address.objects.get(pk=pk)
    except:
        messages.info(request, 'No such address.')
        return redirect('cart')

    data_order_related = checkOrder(order)
    if data_order_related['valid'] == False:
        for key in data_order_related:
            if key != 'valid':
                dic = data_order_related[key]
                print(dic)
                messages.info(request, dic['product'].name + '(' + dic['variant'].name + '): Only' + str(dic['quantity_available']) + 'pieces left.')
        return redirect('cart')

    if request.method == 'POST':
        order_currency = 'INR'
        order_receipt = 'order_'+str(order.pk)
        order_amount, _ = order.get_total_amount_and_quantity()
        order_amount = order_amount*100

        response = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, payment_capture='0'))
        order_id = response['id']
        order_status = response['status']

        if order_status == 'created':
            print('CREATED')
            context = {
                'address': address,
                'order_id': order_id,
                'order': order.pk,
                'amount': order_amount,
                'rzp_key': RP_KEY_ID,
                'name': user.first_name + ' ' + user.last_name,
                'email': user.email,
                'phone': user.customer.phone,
            }
            return render(request, 'order/confirm_order.html', context)


    return render(request, 'order/create_order.html',{
        'address': address,
        'order': order,
        'quantity': order.get_total_amount_and_quantity()[1],
        'amount': order.get_total_amount_and_quantity()[0],
        'order_items': order.orderitem_set.all()
    })


@login_required
def order_summary(request, pk):
    user = request.user
    data = request.POST

    try:
        order = Order.objects.get(customer=user.customer, is_order_placed=False)
    except:
        messages.info(request, 'No item in cart.')
        redirect('cart')

    try:
        address = Address.objects.get(pk=pk)
    except:
        messages.info(request, 'No such address.')
        redirect('cart')


    params_dict = {
        'razorpay_payment_id' : data['razorpay_payment_id'],
        'razorpay_order_id' : data['razorpay_order_id'],
        'razorpay_signature' : data['razorpay_signature']
    }

    # Verifying order status
    try:
        status = client.utility.verify_payment_signature(params_dict)
        order.is_order_placed = True
        order.is_payment_done = True
        order.address = address
        order.date_ordered = datetime.now()
        order.save()

        finaliseOrder(order, user)

        return render(request, 'order/order_summary.html', {'status': 'Payment Successful'})
    except:
        return render(request, 'order/order_summary.html', {'status': 'Payment Faliure!!!'})


@login_required
def pay_with_cod(request, pk):
    user = request.user

    try:
        order = Order.objects.get(customer=user.customer, is_order_placed=False)
    except:
        messages.info(request, 'No item in cart.')
        redirect('cart')

    try:
        address = Address.objects.get(pk=pk)
    except:
        messages.info(request, 'No such address.')
        redirect('cart')
    order.is_order_placed = True
    order.address = address
    order.date_ordered = timezone.localtime(timezone.now())
    order.save()

    finaliseOrder(order, user)
    messages.success(request, 'Order Successfully Placed')
    return redirect('home')

@login_required
def seller_dashboard(request):
    user = request.user
    total_amt = user.seller.amount_for_delivered
    context = {
        'seller': user.seller,
        'total_amount': total_amt,
        'commission': settings.COMMISSION_RATE,
        'you_get': int(total_amt - total_amt * settings.COMMISSION_RATE / 100)
    }

    return render(request, 'order/seller_dashboard.html', context)

@login_required
def seller_orders(request):
    user = request.user

    if not hasattr(user, 'seller'):
        return HttpResponseForbidden('You are not allowed to view this page.')

    orders = OrderItem.objects.values('order', 'order__date_ordered', 'order__date_shipped').filter(variant__product__seller=user.seller, order__is_order_placed = True,).distinct().order_by('-order__date_ordered')
    # shipped_orders = OrderItem.objects.values('order', 'order__date_ordered', 'order__date_shipped', 'order__is_shipped').filter(variant__product__seller=user.seller, order__is_order_placed = True, order__is_shipped=True).distinct().order_by('-order__date_ordered')
    context = {
        'orders': orders,
        # 'shipped_orders': shipped_orders
    }

    return render(request, 'order/seller_orders.html', context)


@login_required
def seller_order_detail(request, pk):
    user = request.user

    try:
        order = Order.objects.get(pk=pk)
    except:
        messages.info(request, 'No such order')
        return redirect('seller-orders')

    order_items = order.orderitem_set.filter(variant__product__seller=user.seller)

    shipped_btn = False
    delivered_btn = False

    total_amt = 0
    you_get = 0
    for item in order_items:
        if not item.is_shipped:
            shipped_btn = True
        elif not item.is_delivered:
            delivered_btn = True
        if not item.is_cancelled and not item.is_return_requested:
            total_amt = total_amt + item.total_amount
            you_get = you_get + item.amt_reducing_commission

    try:
        packaging_pdf = PackagingPDF.objects.get(order=order, seller=user.seller)
    except:
        packaging_pdf = ''

    context = {
        'order': order,
        'order_items': order_items,
        'address': order.address,
        'total_amount': total_amt,
        'you_get': you_get,
        'shipped_btn': shipped_btn,
        'delivered_btn': delivered_btn,
        'packaging_pdf': packaging_pdf
    }

    return render(request, 'order/seller_order_detail.html', context)


@csrf_exempt
def ajax_sent_for_delivery(request):
    user = request.user

    order_id = request.POST.get('order_id')
    unsent = request.POST.get('unsent')
    for_shipping = request.POST.get('for_shipping')
    order = Order.objects.get(pk=order_id)

    order_items = order.orderitem_set.filter(variant__product__seller=user.seller)
    total_amt = 0
    you_get = 0
    for item in order_items:
        if not item.is_cancelled and not item.is_return_requested:
            total_amt = total_amt + item.total_amount
            you_get = you_get + item.amt_reducing_commission

    if for_shipping == 'true':
        if order_items[0].is_delivered:
            user.seller.undelivered(total_amt)
            user.seller.decrease_earning(you_get)
            order_items.update(date_delivered=None)
        if unsent == 'true':
            order_items.update(is_shipped=False, is_delivered=False)
        else:
            order_items.update(is_shipped=True, is_delivered=False)

    else:
        if not order_items[0].is_delivered:
            user.seller.delivered(total_amt)
            user.seller.increase_earning(you_get)
            order_items.update(date_delivered=timezone.localtime(timezone.now()))
        order_items.update(is_shipped=True, is_delivered=True)


    return JsonResponse({'message': 'Status changed successfully', 'type': 'success'})


@login_required
def customer_orders(request):
    user = request.user

    if not hasattr(user, 'customer'):
        return HttpResponseForbidden('You are not allowed to view this page.')

    orders = Order.objects.filter(customer=user.customer).order_by('-date_ordered')
    print(orders)
    context = {
        'orders': orders,
    }

    return render(request, 'order/customer_orders.html', context)


@login_required
def customer_order_detail(request, pk):
    user = request.user

    try:
        order = Order.objects.get(pk=pk)
    except:
        messages.info(request, 'No such order')
        return redirect('customer-orders')

    total_amt = 0
    for item in order.orderitem_set.all():
        if not item.is_cancelled and not item.is_return_requested:
            total_amt = total_amt + item.total_amount

    context = {
        'order': order,
        'address': order.address,
        'order_items': order.orderitem_set.all(),
        'total_amt': total_amt,
    }



    return render(request, 'order/customer_order_detail.html', context)



@csrf_exempt
def ajax_quantity_cart(request):
    user = request.user

    order_item_pk = request.POST.get('order_item_pk', 0)
    increase = request.POST.get('increase')
    if order_item_pk == '':
        return JsonResponse({'message': 'Invalid data.', 'type': 'danger'})

    try:
        order_item = OrderItem.objects.get(pk=order_item_pk)
    except:
        return JsonResponse({'message': 'No such item in cart.', 'type': 'info'})

    order = order_item.order
    if user.is_authenticated:
        if not order_item.order.customer == user.customer:
            return JsonResponse({'message': 'Invalid request', 'type': 'danger'})
    else:
        if not(order.customer == None and order.pk == int(request.COOKIES.get('cart'))):
            return JsonResponse({'message': 'Invalid request', 'type': 'danger'})

    if increase == 'true':
        order_item.quantity = order_item.quantity + 1
    else:
        order_item.quantity = order_item.quantity - 1

    order_item.save()
    item_quantity = order_item.quantity
    item_price = order_item.total_amount
    amount, quantity = order.get_total_amount_and_quantity()
    return JsonResponse({'message': 'Item successfully removed from cart', 'type': 'success', 'change': True, 'quantity':quantity, 'amount': amount, 'item_quantity': item_quantity, 'item_price': item_price})


@login_required
@csrf_exempt
def ajax_cancel_return(request):
    user = request.user

    order_item_pk = request.POST.get('order_item_pk', 0)
    cancel = request.POST.get('cancel')
    if order_item_pk == '':
        return JsonResponse({'message': 'Invalid data.', 'type': 'danger'})

    try:
        order_item = OrderItem.objects.get(pk=order_item_pk)
    except:
        return JsonResponse({'message': 'No such item in cart.', 'type': 'info'})


    if not order_item.order.customer == user.customer:
        return JsonResponse({'message': 'Invalid request', 'type': 'danger'})

    if cancel == 'true':
        bool = order_item.cancel_or_notify()
        if bool:
            order_item.variant.unorder(order_item.quantity)
            return JsonResponse({'message': 'Cancelled', 'type': 'success'})
        else:
            return JsonResponse({'message': 'Invalid request', 'type': 'danger'})

    else:
        bool = order_item.can_return
        if bool:
            order_item.return_item()
            order_item.variant.unorder(order_item.quantity)
            return JsonResponse({'message': 'Return Requested', 'type': 'success'})
        else:
            return JsonResponse({'message': 'Invalid request', 'type': 'danger'})


@login_required
@csrf_exempt
def ajax_return_complete(request):
    user = request.user

    order_item_pk = request.POST.get('order_item_pk', 0)
    if order_item_pk == '':
        return JsonResponse({'message': 'Invalid data.', 'type': 'danger'})

    try:
        order_item = OrderItem.objects.get(pk=order_item_pk)
    except:
        return JsonResponse({'message': 'No such item in cart.', 'type': 'info'})


    if not order_item.variant.product.seller == user.seller:
        return JsonResponse({'message': 'Invalid request', 'type': 'danger'})

    order_item.return_item_complete()
    return JsonResponse({'message': 'Returned', 'type': 'success'})


@csrf_exempt
@login_required
def ajax_add_to_wishlist(request):
    user = request.user

    variant_pk = request.POST.get('variant_pk', None)

    if variant_pk is None:
        return JsonResponse({'message': 'Please select a variant.', 'type': 'info'})

    try:
        variant = Variant.objects.get(pk=variant_pk)
    except:
        return JsonResponse({'message': 'Invalid variant.', 'type': 'info'})

    item, _ = WishlistItem.objects.get_or_create(customer=user.customer, variant=variant)

    return JsonResponse({'message': 'Item successfully added to wishlist.', 'type': 'success'})


@login_required
def wishlist(request):
    user = request.user

    try:

        items = user.customer.wishlistitem_set.all()

        if len(items) == 0:
            raise Exception("Sorry, no numbers below zero")
        context = {
            'wishlist_is_empty': False,
            'items': items,
        }

    except:
        context = {
            'wishlist_is_empty': True,
        }


    return render(request, 'order/wishlist.html', context)

# @login_required
# def invoice(request, pk):
#     user = request.user
#
#     if not hasattr(user, 'customer'):
#         return HttpResponseForbidden('You are not allowed to view this page.')
#
#     try:
#         order = Order.objects.get(pk=pk)
#     except:
#         messages.info(request, 'No such order')
#         return redirect('customer-orders')
#
#     if not order.customer == user.customer:
#         return HttpResponseForbidden('You are not allowed to view this page.')



    # fs = FileSystemStorage(dir)
    # print(fs.url(filename))
    # pdf = fs.url(filename)
    # # with fs.open(filename) as pdf:
    # #     print(fs.url(filename))
    # response = HttpResponse(pdf, content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="'+ filename +'"'
    # return response
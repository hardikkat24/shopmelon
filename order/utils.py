from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
import os

def checkOrder(order):
    """
    Determine whether order can be placed
    """
    data = {}
    data['valid'] = True
    for order_item in order.orderitem_set.all():
        variant = order_item.variant
        if not variant.can_order(order_item.quantity):
            data[variant] = {
                'product': variant.product,
                'variant': variant,
                'quantity_available': variant.quantity_available
            }
            data['valid'] = False
    return data


def finaliseOrder(order, user):
    """
    Decrease the quantity available from models and create invoice
    """

    # create and save invoice
    html_string = render_to_string('order/invoice.html', {
        'order': order,
        'order_items': order.orderitem_set.all(),
        'address': order.address,
        'user': user,
        'total': order.get_total_amount_and_quantity()[0]
    })

    html = HTML(string=html_string)
    dir = os.path.join(settings.BASE_DIR, 'media/invoice/')
    filename = 'Order-' + str(order.id) + '.pdf'
    html.write_pdf(target=dir + filename)

    # set invoice_url for order
    url = settings.MEDIA_URL + 'invoice/' + filename
    order.invoice_url = url
    order.save()

    # Decrease the quantity_available from variants
    for order_item in order.orderitem_set.all():
        variant = order_item.variant
        if variant.can_order(order_item.quantity):
            variant.order(order_item.quantity)
            variant.save()
        else:
            return False


    return True
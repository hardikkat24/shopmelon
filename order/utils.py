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


def finaliseOrder(order):
    """
    Decrease the quantity available from models
    """
    for order_item in order.orderitem_set.all():
        variant = order_item.variant
        if variant.can_order(order_item.quantity):
            variant.order(order_item.quantity)
            variant.save()
        else:
            return False
    return True
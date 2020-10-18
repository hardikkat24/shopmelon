from django.urls import path
from order import views

urlpatterns = [
    path('add-to-cart/', views.ajax_add_to_cart, name='ajax-add-to-cart'),
    path('ajax-add-to-wishlist/', views.ajax_add_to_wishlist, name='ajax-add-to-wishlist'),
    path('cart/', views.cart, name='cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('ajax-delete-from-cart/', views.ajax_delete_from_cart, name='ajax-delete-from-cart'),
    path('place-order/', views.place_order, name='place-order'),
    path('create-order/<pk>/', views.create_order, name='create-order'),
    path('order-summary/<pk>/', views.order_summary, name='order-summary'),
    path('pay-with-cod/<pk>/', views.pay_with_cod, name='pay-with-cod'),

    path('seller-orders/', views.seller_orders, name='seller-orders'),
    path('seller-order/<pk>/', views.seller_order_detail, name='seller-order'),
    path('ajax-sent-for-delivery/', views.ajax_sent_for_delivery, name='ajax-sent-for-delivery'),

    path('customer-orders/', views.customer_orders, name='customer-orders'),
    path('customer-order/<pk>/', views.customer_order_detail, name='customer-order'),

    # path('invoice/<pk>/', views.invoice, name='invoice'),
    path('ajax-quantity-cart/', views.ajax_quantity_cart, name='ajax-quantity-cart'),

    path('seller-dashboard/', views.seller_dashboard, name='seller-dashboard'),
    path('ajax-cancel-return/', views.ajax_cancel_return, name='ajax-cancel-return'),
    path('ajax-return-complete/', views.ajax_return_complete, name='ajax-return-complete'),

]

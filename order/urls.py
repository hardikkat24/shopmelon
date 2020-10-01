from django.urls import path
from order import views

urlpatterns = [
    path('add-to-cart/', views.ajax_add_to_cart, name='ajax-add-to-cart'),
    path('cart/', views.cart, name='cart'),
    path('ajax-delete-from-cart/', views.ajax_delete_from_cart, name='ajax-delete-from-cart'),
]

"""shopmelon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
import product.views as views


urlpatterns = [
    path('add-product/', views.add_product, name='add-product'),
    path('tags/<pk>/', views.tags, name='tags'),
    path('delete-tags/', views.ajax_delete_tags, name='ajax-delete-tags'),

    path('update-product/<pk>/', views.update_product, name='update-product'),
    path('delete-product/<pk>/', views.delete_product, name='delete-product'),

    path('delete-variant/', views.ajax_delete_variant, name='delete-variant'),
    path('product-description/<pk>/', views.product_description, name='product-description'),

    path('search/', views.search, name='search'),

    path('manage-products/', views.manage_products, name='manage-products'),
    path('manage-variants/<pk>/', views.manage_variants, name='manage-variants'),
    path('manage-images/<pk>/', views.manage_images, name='manage-images'),
    path('ajax-delete-image/', views.ajax_delete_image, name='ajax-delete-image'),

]

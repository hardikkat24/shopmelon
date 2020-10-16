from django.urls import path
from django.contrib.auth import views as auth_views

import user.views as views

urlpatterns = [
    # home
    path('home/', views.home, name='home'),

    # signup urls
    path('customer-signup/', views.customer_signup, name='customer-signup'),
    path('seller-signup/', views.seller_signup, name='seller-signup'),

    # login/logout urls
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='user/logout.html'), name='logout'),

    # change password urls
    path('change-password/',auth_views.PasswordChangeView.as_view(template_name='user/change_password.html', success_url='done'),name='change-password'),
    path('change-password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='user/change_password_done.html'), name='change-password-done'),

    # profile related urls
    path('profile/', views.profile, name='profile'),
    path('update-profile/', views.update_profile, name='update-profile'),

    path('resend-email/', views.resend_confirmation_email, name='resend-email'),

    path('activate-seller-home/', views.superuser_activate_seller_home, name='activate-seller-home'),
    path('activate-seller/<pk>/', views.superuser_activate_seller, name='activate-seller'),
]
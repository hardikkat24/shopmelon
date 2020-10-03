from django.urls import path
from django.contrib.auth import views as auth_views

import verification.views as views

urlpatterns = [
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
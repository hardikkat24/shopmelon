from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomerCreationForm, SellerCreationForm


def home(request):
    return render(request, 'user/home.html')


def customer_signup(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        customer_form = CustomerCreationForm(request.POST)
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save()
            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()
            return redirect('home')
    else:
        user_form = CustomUserCreationForm()
        customer_form = CustomerCreationForm()

    context = {
        'user_form': user_form,
        'customer_form': customer_form,
    }
    return render(request, 'user/customer_signup.html', context)


def seller_signup(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        seller_form = SellerCreationForm(request.POST)
        if user_form.is_valid() and seller_form.is_valid():
            user = user_form.save()
            seller = seller_form.save(commit=False)
            seller.user = user
            seller.save()
            return redirect('home')
    else:
        user_form = CustomUserCreationForm()
        seller_form = SellerCreationForm()

    context = {
        'user_form': user_form,
        'seller_form': seller_form,
    }
    return render(request, 'user/seller_signup.html', context)
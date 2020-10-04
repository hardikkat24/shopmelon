from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site

from .forms import CustomUserCreationForm, CustomerCreationForm, SellerCreationForm, CustomUserUpdateForm, EmailResendForm
from verification.verification_utils import send_cofirmation_mail
from user.models import CustomUser
from order.models import Order

def home(request):
    """
    Home page
    """
    return render(request, 'user/home.html')


def customer_signup(request):
    """
    Signup view for Customers
    """
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        customer_form = CustomerCreationForm(request.POST)
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            send_cofirmation_mail(user, current_site)

            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()

            # save cart from cookies if it exists for user as he signs up
            try:
                order = Order.objects.get(pk=request.COOKIES.get('cart'))
                order.customer = customer
                order.save()
            except:
                pass
            messages.success(request, "Profile created successfully! Please confirm you email id.")
            return redirect('login')
    else:
        user_form = CustomUserCreationForm()
        customer_form = CustomerCreationForm()

    context = {
        'user_form': user_form,
        'customer_form': customer_form,
    }
    return render(request, 'user/customer_signup.html', context)


def seller_signup(request):
    """
    Signup view for Sellers
    """
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        seller_form = SellerCreationForm(request.POST)
        if user_form.is_valid() and seller_form.is_valid():
            user = user_form.save()
            seller = seller_form.save(commit=False)
            seller.user = user
            seller.save()
            messages.success(request, "Profile created successfully!")
            return redirect('login')
    else:
        user_form = CustomUserCreationForm()
        seller_form = SellerCreationForm()

    context = {
        'user_form': user_form,
        'seller_form': seller_form,
    }
    return render(request, 'user/seller_signup.html', context)


@login_required
def profile(request):
    """
    Profile view for Customer/Seller/None
    """
    user = request.user

    if hasattr(user, 'customer'):
        customer = user.customer
        context = {
            'user': user,
            'is_customer': True,
            'is_seller': False,
            'customer': customer,
        }
    elif hasattr(user, 'seller'):
        seller = user.seller
        context = {
            'user': user,
            'is_customer': False,
            'is_seller': True,
            'seller': seller,
        }
    else:
        context = {
            'user': user,
            'is_customer': False,
            'is_seller': False,
        }

    return render(request, 'user/profile.html', context)


@login_required
def update_profile(request):
    """
    Update profile view for Customer/Seller/None
    """
    user = request.user

    if request.method == 'POST':
        form1 = CustomUserUpdateForm(request.POST, request.FILES,instance=user)
        is_customer_or_seller = True
        if hasattr(user, 'customer'):
            customer = user.customer
            form2 = CustomerCreationForm(request.POST, request.FILES, instance=customer)
        elif hasattr(user, 'seller'):
            seller = user.seller
            form2 = SellerCreationForm(request.POST, request.FILES, instance=seller)
        else:
            is_customer_or_seller = False
            form2 = None

        if form1.is_valid() and (not is_customer_or_seller or form2.is_valid()) :
            form1.save()
            if is_customer_or_seller:
                form2.save()

            messages.success(request, "Profile updated successfully!")
            return redirect('profile')

    else:
        form1 = CustomUserUpdateForm(instance=user)
        is_customer_or_seller = True
        if hasattr(user, 'customer'):
            customer = user.customer
            form2 = CustomerCreationForm(instance=customer)
        elif hasattr(user, 'seller'):
            seller = user.seller
            form2 = SellerCreationForm(instance=seller)
        else:
            is_customer_or_seller = False
            form2 = None

    context = {
        'form1': form1,
        'form2': form2,
        'is_customer_or_seller': is_customer_or_seller,
    }

    return render(request, 'user/update_profile.html', context)


def resend_confirmation_email(request):
    if request.method == 'POST':
        form = EmailResendForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email', None)
            try:
                user = CustomUser.objects.get(email=email)
                if user.is_active:
                    messages.info(request, 'Email ID already verified')
                else:
                    current_site = get_current_site(request)
                    send_cofirmation_mail(user, current_site)
                    messages.success(request, 'Mail sent successfully, please check your inbox.')
            except:
                messages.info(request, 'Invalid Email ID')
    else:
        form = EmailResendForm()

    context = {
        'form': form
    }

    return render(request, 'user/resend_email.html', context)



def basic_home(request):
    return render(request, 'user/basic_home.html')
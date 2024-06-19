from django.contrib import messages
from django.shortcuts import redirect
from .models import UserAddress

def login_required(func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_anonymous:
            messages.success(request, 'Sorry, You are not logged in. Please Log in.')
            return redirect(to='login')
        else:
            return func(request, *args, **kwargs)
    return wrapper_func

def admin_only(func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_superuser:
            return func(request, *args, **kwargs)
        else:
            messages.warning(request, 'Sorry, You are not authorized to access this page, Please MIND YOUR OWN BUSINESS.')
            return redirect(to='homepage')
    return wrapper_func

def complete_profile(func):
    def wrapper_func(request, *args, **kwargs):
        user = request.user
        if user.phone_no and user.first_name and user.last_name:
            address = UserAddress.objects.filter(user=user)
            if address:
                return func(request, *args, **kwargs)
            else:
                messages.error(request, 'Please provide an address to deliver the product.')
                return redirect(to='edit_profile')
        messages.error(request, 'Please provide your contact information for delivery purpose and address if not provided.')
        return redirect(to='edit_profile')
    return wrapper_func
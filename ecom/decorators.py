from django.contrib import messages
from django.shortcuts import redirect

def login_required(func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_anonymous:
            messages.success(request, 'Sorry, You are not logged in. Please Log in')
            return redirect(to='login')
        else:
            return func(request, *args, **kwargs)
    return wrapper_func

def admin_only(func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_superuser:
            return func(request, *args, **kwargs)
        else:
            messages.warning(request, 'Sorry, You are not authorized to access this page, Please MIND YOUR OWN BUSINESS')
            return redirect(to='homepage')
    return wrapper_func
from django.contrib import messages
from django.shortcuts import redirect

def login_required(func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_anonymous:
            messages.success(request, 'Sorry, You are not logged in.\nPlease Log in')
            return redirect(to='login')
        else:
            return func(request, *args, **kwargs)
    return wrapper_func
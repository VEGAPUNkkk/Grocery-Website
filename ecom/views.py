from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import CreateUserForm, LoginForm, UserDetailForm
from django.conf import settings
from django.contrib import messages
from .helper import authenticate
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.hashers import make_password
# Create your views here.

def homepage(request):
    products = Product.objects.all()[:3]
    return render(request, 'ecom/index.html', {'products' : products})

def product_list(request):
    products = Product.objects.all()
    categories = Product.objects.values_list('category', flat=True).distinct()
    return render(request, 'ecom/product.html', {'products' : products, 'categories' : categories})

def signupPage(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data.get("password"))
            already_user = authenticate(username=form.cleaned_data.get("username"), password=form.cleaned_data.get("password"))
            if already_user is not None:
                if already_user.username == form.cleaned_data.get("username"):
                    messages.info(request, 'Username already taken')
                elif already_user.email == form.cleaned_data.get("email"):
                    messages.error(request, 'User already exists login instead')
                    return redirect('login')
            user.save()
            messages.success(request, 'User created successfully, Please Login')
            return redirect(to='login')
    else:
        form = CreateUserForm()
    return render(request, 'ecom/signup.html', {'form' : form})

def loginPage(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(to='homepage')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'ecom/login.html', {'form' : form})

def logoutUser(request):
    logout(request)
    return redirect(to='homepage')

def aboutUs(request):
    return render(request, 'ecom/about.html', {})

def profile(request):
    user = request.user
    return render(request, 'ecom/profile.html', {'user' : user})

def edit_profile(request):
    if request.method == 'POST':
        form = UserDetailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(to='profile')
    else:
        form = UserDetailForm(instance=request.user)
    return render(request, 'ecom/edit_profile.html', {'form': form})

def add_to_cart(request, id, op=None):
    quantity = int(request.GET.get('quantity', 1))
    print('\n\n', quantity,op, '\n\n')
    user = request.user
    product = get_object_or_404(Product, pk=id)
    cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
    if created:
        cart_item.quantity = quantity
    else:
        if op=='sub':
            cart_item.quantity -= quantity
        else:
            cart_item.quantity += quantity
    cart_item.save()
    return redirect(to='view_cart')

def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    products = []
    total_price = 0

    for item in cart_items:
        product = item.product
        total_price += product.price * item.quantity
        products.append({
            'product': product,
            'quantity': item.quantity,
            'total_price': product.price * item.quantity
        })

    return render(request, 'ecom/cart.html', {'products': products, 'total_price': total_price})


def remove_from_cart(request, id):
    cart_item = CartItem.objects.get(user=request.user, product_id=id)
    cart_item.delete()
    return redirect(to='view_cart')
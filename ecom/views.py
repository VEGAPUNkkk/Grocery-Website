from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import CreateUserForm, LoginForm, UserDetailForm
from django.conf import settings
from django.contrib import messages
from .helper import authenticate
from django.contrib.auth import login, logout, get_user_model
from .decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
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

@login_required
def profile(request):
    user = request.user
    return render(request, 'ecom/profile.html', {'user' : user})
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserDetailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(to='profile')
    else:
        form = UserDetailForm(instance=request.user)
    return render(request, 'ecom/edit_profile.html', {'form': form})
@login_required
def add_to_cart(request, id, op=None):
    quantity = int(request.GET.get('quantity', 1))
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
@login_required
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

@login_required
def remove_from_cart(request, id):
    cart_item = CartItem.objects.get(user=request.user, product_id=id)
    cart_item.delete()
    return redirect(to='view_cart')

@login_required
def add_to_orders(request, id):
    quantity = int(request.GET.get('quantity', 1))
    product = get_object_or_404(Product, pk=id)
    user = request.user
    Orders.objects.create(
        product = product,
        user=user,
        quantity = quantity,
        total_price = quantity * product.price
    )
    return redirect(to='view_orders')

@login_required
def view_orders(request):
    order_items = Orders.objects.filter(user=request.user)
    products = []
    total_price = 0
    for items in order_items:
        product = items.product
        total_price += product.price * items.quantity
        products.append({
            'product' : product,
            'quantity' : items.quantity,
            'total_price' : product.price * items.quantity
        })  
    return render(request, 'ecom/orders.html', {'products' : products, 'total_price' : total_price})

@login_required
def cancel_order(request, id):
    order_item = get_object_or_404(Orders, user=request.user, product_id=id)
    order_item.delete()
    return redirect(to='view_orders')

@login_required
def contact_form(request):
    if request.method == "POST":
        user = request.user
        name = user.username
        email = user.email
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        full_message = f"Message from {name}, {email}:\n\n{subject}\n{message}"
        send_mail(
            subject,
            full_message,
            email,
            ['monkeydluffy7038@gmail.com'],
        )
        messages.success(request, 'Message sent successfully')
        return redirect(to='homepage')
    
def search(request):
    if request.method == "POST":
        search_item = request.POST.get('search')
        products = Product.objects.filter(name__contains=search_item)
        if products:
            product_category = Product.objects.values_list('category', flat=True).distinct()
            categories = []
            for i in range(len(products)):
                if product_category[i] == products[i].category:
                    categories.append(product_category[i])
            return render(request, 'ecom/product.html', {'products' : products, 'categories' : categories})
        product_category = Product.objects.filter(category__contains=search_item)
        if product_category:
            print(product_category)
            return render(request, 'ecom/product.html', {'products' : product_category, 'categories' : [product_category[0].category]})
        else:
            return render(request, 'ecom/product.html', {})
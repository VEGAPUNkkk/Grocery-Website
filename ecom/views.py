from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import CreateUserForm, LoginForm, UserDetailForm, AddressForm
from django.conf import settings
from django.contrib import messages
from .helper import authenticate, send_message
from django.contrib.auth import login, logout, get_user_model
from .decorators import login_required, admin_only, complete_profile
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
import csv
import os
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

@login_required
def logoutUser(request):
    logout(request)
    return redirect(to='homepage')

def aboutUs(request):
    return render(request, 'ecom/about.html', {})

@login_required
def profile(request):
    user = request.user
    user_address = UserAddress.objects.filter(user=user)
    if user_address:
        for address in user_address:
           add =  f"{address.residence}, {address.landmark}, {address.street}, {address.city}, {address.state}, {address.postal_code}, {address.country}"
        return render(request, 'ecom/profile.html', {'user' : user, 'add' : add})
    return render(request, 'ecom/profile.html', {'user' : user})

@login_required
def edit_profile(request):
    user = request.user
    address = UserAddress.objects.filter(user=user).first()
    if request.method == 'POST':
        profile_form = UserDetailForm(request.POST, instance=user)
        address_form = AddressForm(request.POST)

        if profile_form.is_valid(): 
            profile_form.save()

        else:
            messages.error(request, "Some field that you entered is not valid or is already taken by another user (For example: email, username or phone number)")
            return redirect(to='edit_profile')
        
        if address_form.is_valid():
            user_address, created = UserAddress.objects.get_or_create(user=user)
            if created:
                user = user
                user_address.residence = address_form.cleaned_data.get('residence')
                user_address.landmark = address_form.cleaned_data.get('landmark')
                user_address.street = address_form.cleaned_data.get('street')
                user_address.city = address_form.cleaned_data.get('city')
                user_address.state = address_form.cleaned_data.get('state')
                user_address.country = address_form.cleaned_data.get('country')
                user_address.postal_code = address_form.cleaned_data.get('postal_code')
            else:
                user = user,
                user_address.residence = request.POST.get('residence')
                user_address.landmark = address_form.cleaned_data.get('landmark')
                user_address.street = address_form.cleaned_data.get('street')
                user_address.city = address_form.cleaned_data.get('city')
                user_address.state = address_form.cleaned_data.get('state')
                user_address.country = address_form.cleaned_data.get('country')
                user_address.postal_code = address_form.cleaned_data.get('postal_code')
            user_address.save()   
        return redirect(to='profile')
    else:
        profile_form = UserDetailForm(instance=user)
        #Can provide address instance if wanted
        address_form = AddressForm()
        return render(request, 'ecom/edit_profile.html', {'profile_form': profile_form, 'address_form' : address_form})

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
@complete_profile
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

    send_message(user=request.user, subject='place', product=product, quantity=quantity)

    return redirect(to='view_orders')

@login_required
@complete_profile
def buy_all(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    for item in cart_items:
        product = Product.objects.get(pk=item.product.id)
        quantity = item.quantity
        total_price = quantity * product.price
        Orders.objects.create(
            product = product,
            user = user,
            quantity = quantity,
            total_price = total_price
        )
        send_message(user=request.user, subject='place', product=product, quantity=quantity)
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
            'pk' : items.pk,
            'product' : product,
            'quantity' : items.quantity,
            'total_price' : product.price * items.quantity
        }) 
    return render(request, 'ecom/orders.html', {'products' : products, 'total_price' : total_price})

@login_required
def cancel_order(request, id):
    user = request.user
    print(id)
    order_item = get_object_or_404(Orders, user=user, pk=id)
    product = get_object_or_404(Product, pk=order_item.product_id)

    send_message(user=request.user, subject='cancel', product=product, quantity=order_item.quantity)

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
        
@login_required
def order_details(request):
    user = request.user
    if not user.is_superuser:
        messages.warning(request, 'Sorry, You are not authorized to access this page, Please MIND YOUR OWN BUSINESS')
        return render(request, 'ecom/order_details.html', {})
    
    else:
        products = []
        mydict = []
        orders = Orders.objects.all()
        for order in orders:
            product = Product.objects.get(pk=order.product_id)
            current_user = User.objects.get(pk=order.user_id)
            address = UserAddress.objects.get(user=current_user)
            add =  f"{address.residence}, {address.landmark}, {address.street}, {address.city}, {address.state}, {address.postal_code}, {address.country}"
            total_price = order.quantity * order.total_price
            products.append({
                'product' : product,
                'user' : current_user,
                'order' : order,
                'address' : add,
                'total_price' : total_price
            })

            mydict.append({
                'username' : current_user.username,
                'address' : add,
                'phone_no' : current_user.phone_no,
                'product' : product.name,
                'quantity' : order.quantity,
                'total_price' : total_price
            })
        
        fields = ['username', 'address', 'phone_no', 'product', 'quantity', 'total_price']
        with open('media/ecom/files/orders.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            writer.writerows(mydict)

        file_url = os.path.join(settings.MEDIA_URL, 'ecom', 'files', 'orders.csv')
        return render(request, 'ecom/order_details.html', {'products' : products, 'file_url' : file_url})
        
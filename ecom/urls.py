from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('products/', views.product_list, name='product_list'),
    path('signup/', views.signupPage, name='signup'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('about/', views.aboutUs, name='aboutUs'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('add_to_cart/<int:id>/<op>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add_to_orders/<int:id>/', views.add_to_orders, name='add_to_orders'),
    path('view_orders/', views.view_orders, name='view_orders'),
    path('cancel_order/<int:id>/', views.cancel_order, name='cancel_order'),
    path('contact_form', views.contact_form, name='contact_form'),
    path('search', views.search, name='search'),
    path('order_details/', views.order_details, name='order_details'),
    path('buy_all/', views.buy_all, name='buy_all'),
]
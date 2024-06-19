from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserAddress
from django import forms


class CreateUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']
    
class UserDetailForm(forms.ModelForm):

    class Meta:
        model = User 
        fields = ['username', 'email', 'firstname', 'lastname',  'phone_no']

class AddressForm(forms.ModelForm):

    class Meta:
        model = UserAddress
        fields = ['residence', 'landmark', 'street', 'city', 'state', 'country', 'postal_code']
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from .models import User


def authenticate(username=None, password=None):
    try:
        # Get the corresponding user.
        user = User.objects.get(username=username)
        #  If password, matches just return the user. Otherwise, return None.
        if check_password(password, user.password):
            return user
        return None
    except User.DoesNotExist:
        # No user was found.
        return None
    
def send_message(user, subject, product, quantity):
    user = user
    name = user.username
    email = user.email
    if subject == 'place':
        subject = "Product Order"
        message = f"User {user.username} has ordered {product.name} \n Quantity: {quantity} \n Total Price: {quantity * product.price}"
    else:
        subject = "Product Cancel"
    message = f"User {user.username} has canceled {product.name} \n Quantity: {quantity} \n Total Price: {quantity * product.price}"
    full_message = f"Message from {name}, {email}:\n\n{subject}\n{message}"
    send_mail(
        subject,
        full_message,
        email,
        ['mashburnedead7038@gmail.com'],
    )
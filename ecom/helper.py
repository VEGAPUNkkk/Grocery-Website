from django.contrib.auth.hashers import check_password

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
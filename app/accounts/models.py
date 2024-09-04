from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model in case we need to add more fields in the future"""
    pass

from django import forms
from django_registration.forms import RegistrationForm
from .models import User

class CustomUserRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User
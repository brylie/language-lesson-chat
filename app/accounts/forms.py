from django_registration.forms import RegistrationForm
from .models import User


class CustomRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User
        # You can adjust these fields as needed
        fields = ['username', 'email', 'password1', 'password2']

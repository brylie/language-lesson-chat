from django.shortcuts import render
from django.urls import reverse_lazy
from django_registration.backends.one_step.views import RegistrationView
from .forms import CustomUserRegistrationForm
# Create your views here.
# def signup(request):
#     # logic here
#     return render(request, 'signup.html')

# def registration_complete(request):
#     return render(request, 'registration_complete.html')

# class CustomRegistrationView(RegistrationView):
#     success_url = reverse_lazy('registration_complete')
#     template_name = "django_registration/registration_form.html"

class CustomRegistrationView(RegistrationView):
    form_class = CustomUserRegistrationForm
from django.shortcuts import render
from .models import Account
from .forms import RegistrationForm

# Create your views here.

def register (request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
           first_name = form.cleaned_data.get('first_name')
           last_name = form.cleaned_data.get('last_name')
           email = form.cleaned_data.get('email')
        #    phone_number = form.cleaned_data.get('phone_number')
           password1 = form.cleaned_data.get('password1')
           password2 = form.cleaned_data.get('password2')
           
           if password1 == password2:
               pass
           else:
               form.add_error('password2', 'Passwords do not match')

        user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=email.split('@')[0], password=password1)
        user.save()
    else:
        form = RegistrationForm()
        
    context = {
        'form': form,
    }
    return render (request, 'accounts/register.html', context)

def login (request):
    return render(request, 'accounts/login.html')

def logout (request):
    return render (request, 'accounts/logout.html')
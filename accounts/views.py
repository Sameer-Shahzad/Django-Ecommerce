import re
from django.forms import ValidationError
from django.shortcuts import redirect, render
from .models import Account
from .forms import RegistrationForm
from django.contrib import messages

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')

            if not re.match(r'^[a-zA-Z\s]+$', first_name):
                form.add_error('first_name', "Name should only contain letters!")
            
            if not re.match(r'^[a-zA-Z\s]+$', last_name):
                form.add_error('last_name', "Last name should only contain letters!")

            if Account.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already registered!')

            if password1 != password2:
                form.add_error('password2', 'Passwords do not match!')

            if not form.errors:
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                while Account.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = Account.objects.create_user(
                    first_name=first_name, 
                    last_name=last_name, 
                    email=email, 
                    username=username, 
                    password=password1
                )
                user.save()
                messages.success(request, 'Account created successfully!')
                return redirect('register')
            
            
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
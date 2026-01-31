import re
from django.forms import ValidationError
from django.shortcuts import redirect, render
from .models import Account
from .forms import RegistrationForm
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse

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
                
                # User Activation through Email 
                current_site = get_current_site(request)
                mail_subject = 'Please activate your account'
                message = render_to_string('accounts/account_verification_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = email
                
                send_email = EmailMessage (mail_subject, message, to=[to_email])
                
                messages.success(request, 'Account created successfully!')
                return redirect('register')
            
            
    else:
        form = RegistrationForm()
        
    context = {
        'form': form,
    }
    return render (request, 'accounts/register.html', context)

def login (request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = auth.authenticate(request, username=email, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
        
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout (request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    
    return redirect('login')


def activate (request, uidb64, token):
    return HttpResponse("Activate Account")
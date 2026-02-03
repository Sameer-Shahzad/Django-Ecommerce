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
    if request.user.is_authenticated:
        return redirect('home')
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

                send_email.send()
                
                messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address. Please verify to activate your account.')
                return redirect('register')        
    else:
        form = RegistrationForm()
        
    context = {
        'form': form,
    }
    return render (request, 'accounts/register.html', context)

def login (request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = auth.authenticate(request, username=email, password=password)
            
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')
            return render('login')
        
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout (request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    
    
@login_required(login_url='login')
def dashboard (request):
    return render (request, 'accounts/dashboard.html')


def forgotPassword (request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            
            send_email = EmailMessage (mail_subject, message, to=[to_email])

            send_email.send()
            
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:  
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
        
    return render (request, 'accounts/forgotPassword.html')



def reset_password_validator(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
       request.session['uid'] = uidb64
       messages.success(request, 'Please reset your password')
       return redirect('resetPassword') 
       
    else:
        messages.error(request, 'The reset password link is invalid, please request a new one.')
        return redirect('forgotPassword')
       
       
def resetPassword (request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':  
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save() 
            messages.success(request, 'Password reset successful. You can now log in with your new password.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('resetPassword')
    return render (request, 'accounts/resetPassword.html')
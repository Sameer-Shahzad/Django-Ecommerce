from django import forms
from .models import Account



class RegistrationForm (forms.ModelForm):
    
    password1 = forms.CharField (widget = forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))
    password2 = forms.CharField (widget = forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email']
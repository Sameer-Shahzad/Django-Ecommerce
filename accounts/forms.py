from django import forms
from .models import Account

from django.core.exceptions import ValidationError

class RegistrationForm (forms.ModelForm):
    
    password1 = forms.CharField (widget = forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))
    password2 = forms.CharField (widget = forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email']
        
        

class UserPasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("New passwords do not match!")
        
        if new_password and len(new_password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
            
        return cleaned_data
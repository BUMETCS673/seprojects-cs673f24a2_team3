from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

class RegistrationForm(forms.Form):
    account_name = forms.CharField(
        max_length=150,
        help_text="Enter any combination of letters, numbers, or symbols.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter account name'
        })
    )
    user_id = forms.CharField(
        max_length=10,
        min_length=10,
        help_text="Enter a unique 10-digit number.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter user ID'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),
        help_text="Password must be at least 8 characters, with at least one uppercase letter, one lowercase letter, one digit, and one symbol."
    )

def clean_user_id(self):
    user_id = self.cleaned_data['user_id']
    if not user_id.isdigit():
        raise ValidationError("User ID must consist of numbers only.")
    if len(user_id) != 10:
        raise ValidationError("User ID must be exactly 10 digits long.")
    if User.objects.filter(profile__user_id=user_id).exists():
        raise ValidationError("This User ID is already in use.")
    return user_id

def clean_password(self):
    password = self.cleaned_data['password']
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must include at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must include at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must include at least one digit.")
    if not re.search(r"\W", password):
        raise ValidationError("Password must include at least one symbol.")
    return password



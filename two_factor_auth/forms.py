# two_factor_auth/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm

class AuthenticationForm(DjangoAuthenticationForm):
    username = forms.EmailField(max_length=254, widget=forms.TextInput(attrs={'autocomplete': 'email'}))
    password = forms.CharField(label=("Password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))



class OTPForm(forms.Form):
    otp_code = forms.CharField(label='Codice OTP', max_length=6)
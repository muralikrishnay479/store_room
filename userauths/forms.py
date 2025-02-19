from django import forms
from django.contrib.auth.forms import UserCreationForm

from captcha.fields import CaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from userauths.models import User

USER_TYPE = (
    ("Customer", "Customer"),
    ("Vendor", "Vendor"),
)
class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control rounded',
        'placeholder': 'Full Name',
    }))
    mobile = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control rounded',
        'placeholder': 'Mobile number',
    }))
    email = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control rounded',
        'placeholder': 'Email',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control rounded',
        'placeholder': 'Enter Password',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control rounded',
        'placeholder': 'Confirm Password',
    }))
    captcha = CaptchaField()
    user_type = forms.ChoiceField(choices=USER_TYPE, widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = User
        fields = ['full_name', 'mobile','email', 'password1', 'password2' , 'user_type', 'captcha']


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control rounded form-control',
        'placeholder': 'Email',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control rounded form-control',
        'placeholder': 'Password',
    }))
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ['email', 'password', 'captcha']


from django import forms
from django.contrib.auth.forms import PasswordResetForm

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control rounded',
        'placeholder': 'Enter your email address',
    }))

    class Meta:
        fields = ['email']
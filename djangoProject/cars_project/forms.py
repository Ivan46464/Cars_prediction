
from django import forms

class CarForm(forms.Form):
    image = forms.ImageField()
    model = forms.CharField(label='Model', max_length=100)
    year = forms.CharField(label='Year', max_length=100)
    mileage = forms.CharField(label='Mileage', max_length=100)

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)

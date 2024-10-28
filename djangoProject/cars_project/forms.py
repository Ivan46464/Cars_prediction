from django import forms

class CarForm(forms.Form):
    image = forms.ImageField()
    model = forms.CharField(label='Model', max_length=100)
    year = forms.CharField(label='Year', max_length=100)
    mileage = forms.CharField(label='Mileage', max_length=100)


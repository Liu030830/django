from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Product
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone', 'address', 'quantity']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'quantity': forms.NumberInput(attrs={'min': 1})
        }


class RegisterForm(UserCreationForm):
    is_merchant = forms.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'is_merchant']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

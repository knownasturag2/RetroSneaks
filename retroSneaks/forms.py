from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Shoe, CustomizationPrice, CartItem, Order

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom styling to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue'
            })

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom styling to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue'
            })

class CustomizationForm(forms.Form):
    shoe = forms.ModelChoiceField(
        queryset=Shoe.objects.all(),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg'})
    )
    base_color = forms.ModelChoiceField(
        queryset=CustomizationPrice.objects.filter(customization_type='base_color', active=True),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg'})
    )
    accent_color = forms.ModelChoiceField(
        queryset=CustomizationPrice.objects.filter(customization_type='accent_color', active=True),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg'})
    )
    sole_pattern = forms.ModelChoiceField(
        queryset=CustomizationPrice.objects.filter(customization_type='pattern', active=True),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg'})
    )
    quantity = forms.IntegerField(
        min_value=1, 
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg'})
    )

class CartItemForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1)
    size = forms.ChoiceField(choices=Shoe.SIZE_CHOICES)
    
    class Meta:
        model = CartItem
        fields = ['quantity']

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'payment_method']
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg',
                'rows': 3
            }),
            'payment_method': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg'
            })
        }

class NewsletterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'px-4 py-2 w-full text-gray-800 rounded-l focus:outline-none',
            'placeholder': 'Your email'
        })
    )
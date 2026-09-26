from django import forms

from .models import Product, Stock


class StockForm(forms.ModelForm):

    class Meta:
        model = Stock

        fields = [
            'product',
            'location',
            'quantity',
        ]

        widgets = {
            'product': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'location': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter quantity',
                    'min': '0',
                    'step': '0.01',
                }
            ),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if quantity < 0:
            raise forms.ValidationError(
                'Quantity cannot be negative.'
            )

        return quantity
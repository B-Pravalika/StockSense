from django import forms

from .models import Category, Product,Stock


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'sku',
            'category',
            'unit_of_measure',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name',
            }),

            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter SKU',
            }),

            'category': forms.Select(attrs={
                'class': 'form-control',
            }),

            'unit_of_measure': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: Pieces',
            }),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'name',
            'description',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category description',
                'rows': 4,
            }),
        }

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'product',
            'location',
            'quantity',
        ]

        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),

            'location': forms.Select(attrs={
                'class': 'form-control',
            }),

            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
        }
from django import forms

from .models import Location, Warehouse


class WarehouseForm(forms.ModelForm):

    class Meta:
        model = Warehouse

        fields = [
            'name',
            'address',
        ]

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter warehouse name',
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter warehouse address',
                    'rows': 4,
                }
            ),
        }


class LocationForm(forms.ModelForm):

    class Meta:
        model = Location

        fields = [
            'warehouse',
            'name',
        ]

        widgets = {
            'warehouse': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Example: Storage',
                }
            ),
        }
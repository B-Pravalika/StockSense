from django import forms

from .models import (
    AdjustmentItem,
    Delivery,
    DeliveryItem,
    InternalTransfer,
    InventoryAdjustment,
    Receipt,
    ReceiptItem,
    Supplier,
    TransferItem,
)


class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier

        fields = [
            'name',
            'contact_person',
            'phone',
            'email',
            'address',
        ]

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter supplier name',
                }
            ),

            'contact_person': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter contact person',
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter phone number',
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter email address',
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter supplier address',
                    'rows': 4,
                }
            ),
        }


class ReceiptForm(forms.ModelForm):

    class Meta:
        model = Receipt

        fields = [
            'reference',
            'supplier',
            'destination',
            'scheduled_date',
            'notes',
        ]

        widgets = {
            'reference': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Example: REC-001',
                }
            ),

            'supplier': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'destination': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'scheduled_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Optional notes',
                    'rows': 4,
                }
            ),
        }


class ReceiptItemForm(forms.ModelForm):

    class Meta:
        model = ReceiptItem

        fields = [
            'product',
            'quantity',
        ]

        widgets = {
            'product': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter quantity',
                    'min': '0.01',
                    'step': '0.01',
                }
            ),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if quantity <= 0:
            raise forms.ValidationError(
                'Quantity must be greater than zero.'
            )

        return quantity



class DeliveryForm(forms.ModelForm):

    class Meta:
        model = Delivery

        fields = [
            'reference',
            'destination',
            'source_location',
            'scheduled_date',
            'notes',
        ]

        widgets = {
            'reference': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Example: DEL-001',
                }
            ),

            'destination': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter customer/destination',
                }
            ),

            'source_location': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'scheduled_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Optional notes',
                    'rows': 4,
                }
            ),
        }


class DeliveryItemForm(forms.ModelForm):

    class Meta:
        model = DeliveryItem

        fields = [
            'product',
            'quantity',
        ]

        widgets = {
            'product': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter quantity',
                    'min': '0.01',
                    'step': '0.01',
                }
            ),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if quantity <= 0:
            raise forms.ValidationError(
                'Quantity must be greater than zero.'
            )

        return quantity

class InternalTransferForm(forms.ModelForm):

    class Meta:
        model = InternalTransfer

        fields = [
            'reference',
            'source_location',
            'destination_location',
            'scheduled_date',
            'notes',
        ]

        widgets = {
            'reference': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Example: TRF-001',
                }
            ),

            'source_location': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'destination_location': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'scheduled_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Optional notes',
                    'rows': 4,
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        source = cleaned_data.get('source_location')
        destination = cleaned_data.get('destination_location')

        if (
            source is not None
            and destination is not None
            and source == destination
        ):
            raise forms.ValidationError(
                'Source and destination locations must be different.'
            )

        return cleaned_data


class TransferItemForm(forms.ModelForm):

    class Meta:
        model = TransferItem

        fields = [
            'product',
            'quantity',
        ]

        widgets = {
            'product': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter quantity',
                    'min': '0.01',
                    'step': '0.01',
                }
            ),
        }

    def clean_quantity(self):

        quantity = self.cleaned_data['quantity']

        if quantity <= 0:
            raise forms.ValidationError(
                'Quantity must be greater than zero.'
            )

        return quantity

class InventoryAdjustmentForm(forms.ModelForm):

    class Meta:
        model = InventoryAdjustment

        fields = [
            'reference',
            'location',
            'reason',
        ]

        widgets = {
            'reference': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Example: ADJ-001',
                }
            ),

            'location': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'reason': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter reason for adjustment',
                    'rows': 4,
                }
            ),
        }


class AdjustmentItemForm(forms.ModelForm):

    class Meta:
        model = AdjustmentItem

        fields = [
            'product',
            'counted_quantity',
        ]

        widgets = {
            'product': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'counted_quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter physically counted quantity',
                    'min': '0',
                    'step': '0.01',
                }
            ),
        }

    def clean_counted_quantity(self):

        quantity = self.cleaned_data['counted_quantity']

        if quantity < 0:
            raise forms.ValidationError(
                'Counted quantity cannot be negative.'
            )

        return quantity

from django import forms

from .models import ReorderRule


class ReorderRuleForm(forms.ModelForm):
    class Meta:
        model = ReorderRule
        fields = [
            'product',
            'location',
            'minimum_quantity',
            'maximum_quantity',
            'reorder_quantity',
            'is_active',
        ]

        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),

            'location': forms.Select(attrs={
                'class': 'form-control',
            }),

            'minimum_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Example: 10',
            }),

            'maximum_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Example: 100',
            }),

            'reorder_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Example: 50',
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        minimum = cleaned_data.get('minimum_quantity')
        maximum = cleaned_data.get('maximum_quantity')
        reorder = cleaned_data.get('reorder_quantity')

        if (
            minimum is not None
            and maximum is not None
            and maximum < minimum
        ):
            raise forms.ValidationError(
                'Maximum quantity must be greater than or equal to minimum quantity.'
            )

        if reorder is not None and reorder <= 0:
            raise forms.ValidationError(
                'Reorder quantity must be greater than zero.'
            )

        return cleaned_data
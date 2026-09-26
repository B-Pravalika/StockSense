from django.db import models

from inventory.models import Product
from warehouse.models import Location


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Receipt(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('WAITING', 'Waiting'),
        ('READY', 'Ready'),
        ('DONE', 'Done'),
        ('CANCELED', 'Canceled'),
    ]

    reference = models.CharField(
        max_length=50,
        unique=True
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='receipts'
    )

    destination = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='receipts'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    scheduled_date = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference} - {self.supplier.name}"


class ReceiptItem(models.Model):
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='receipt_items'
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.receipt.reference} - {self.product.name}"

class Delivery(models.Model):

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('WAITING', 'Waiting'),
        ('READY', 'Ready'),
        ('PICK', 'Pick'),
        ('PACK', 'Pack'),
        ('DONE', 'Done'),
        ('CANCELED', 'Canceled'),
    ]

    reference = models.CharField(
        max_length=50,
        unique=True
    )

    destination = models.CharField(
        max_length=200
    )

    source_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='deliveries'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    scheduled_date = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference} - {self.destination}"


class DeliveryItem(models.Model):

    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='delivery_items'
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.delivery.reference} - {self.product.name}"

class InternalTransfer(models.Model):

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('WAITING', 'Waiting'),
        ('READY', 'Ready'),
        ('DONE', 'Done'),
        ('CANCELED', 'Canceled'),
    ]

    reference = models.CharField(
        max_length=50,
        unique=True
    )

    source_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='outgoing_transfers'
    )

    destination_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='incoming_transfers'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    scheduled_date = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.reference}: "
            f"{self.source_location} → "
            f"{self.destination_location}"
        )


class TransferItem(models.Model):

    transfer = models.ForeignKey(
        InternalTransfer,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='transfer_items'
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.transfer.reference} - {self.product.name}"
class InventoryAdjustment(models.Model):

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('DONE', 'Done'),
        ('CANCELED', 'Canceled'),
    ]

    reference = models.CharField(
        max_length=50,
        unique=True
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='adjustments'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reference


class AdjustmentItem(models.Model):

    adjustment = models.ForeignKey(
        InventoryAdjustment,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='adjustment_items'
    )

    counted_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return (
            f"{self.adjustment.reference} - "
            f"{self.product.name}"
        )

class StockLedger(models.Model):

    OPERATION_CHOICES = [
        ('RECEIPT', 'Receipt'),
        ('DELIVERY', 'Delivery'),
        ('TRANSFER_IN', 'Transfer In'),
        ('TRANSFER_OUT', 'Transfer Out'),
        ('ADJUSTMENT', 'Adjustment'),
    ]

    reference = models.CharField(max_length=50)

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='ledger_entries'
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='ledger_entries'
    )

    operation = models.CharField(
        max_length=20,
        choices=OPERATION_CHOICES
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.reference} - "
            f"{self.product.name} - "
            f"{self.operation}"
        )

class ReorderRule(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reorder_rules'
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='reorder_rules'
    )

    minimum_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    maximum_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    reorder_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'location'],
                name='unique_reorder_rule_product_location'
            )
        ]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.location.name}"
        )
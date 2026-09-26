from django.contrib import admin

from .models import (
    Supplier,
    Receipt,
    ReceiptItem,
    Delivery,
    DeliveryItem,
    InternalTransfer,
    TransferItem,
    InventoryAdjustment,
    AdjustmentItem,
    StockLedger,
    ReorderRule,
)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'contact_person',
        'phone',
        'email',
    )
    search_fields = (
        'name',
        'contact_person',
        'phone',
        'email',
    )


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'supplier',
        'destination',
        'status',
        'scheduled_date',
    )
    search_fields = (
        'reference',
        'supplier__name',
    )
    list_filter = (
        'status',
        'scheduled_date',
    )


@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    list_display = (
        'receipt',
        'product',
        'quantity',
    )
    search_fields = (
        'receipt__reference',
        'product__name',
        'product__sku',
    )


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'destination',
        'source_location',
        'status',
        'scheduled_date',
    )
    search_fields = (
        'reference',
        'destination',
    )
    list_filter = (
        'status',
        'scheduled_date',
    )


@admin.register(DeliveryItem)
class DeliveryItemAdmin(admin.ModelAdmin):
    list_display = (
        'delivery',
        'product',
        'quantity',
    )
    search_fields = (
        'delivery__reference',
        'product__name',
        'product__sku',
    )


@admin.register(InternalTransfer)
class InternalTransferAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'source_location',
        'destination_location',
        'status',
        'scheduled_date',
    )
    search_fields = (
        'reference',
    )
    list_filter = (
        'status',
        'scheduled_date',
    )


@admin.register(TransferItem)
class TransferItemAdmin(admin.ModelAdmin):
    list_display = (
        'transfer',
        'product',
        'quantity',
    )
    search_fields = (
        'transfer__reference',
        'product__name',
        'product__sku',
    )


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'location',
        'status',
        'created_at',
    )
    search_fields = (
        'reference',
        'location__name',
    )
    list_filter = (
        'status',
    )


@admin.register(AdjustmentItem)
class AdjustmentItemAdmin(admin.ModelAdmin):
    list_display = (
        'adjustment',
        'product',
        'counted_quantity',
    )
    search_fields = (
        'adjustment__reference',
        'product__name',
        'product__sku',
    )


@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'product',
        'location',
        'operation',
        'quantity',
        'created_at',
    )
    search_fields = (
        'reference',
        'product__name',
        'product__sku',
    )
    list_filter = (
        'operation',
        'location',
    )
    readonly_fields = (
        'created_at',
    )


@admin.register(ReorderRule)
class ReorderRuleAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'location',
        'minimum_quantity',
        'maximum_quantity',
        'reorder_quantity',
        'is_active',
    )
    search_fields = (
        'product__name',
        'product__sku',
        'location__name',
    )
    list_filter = (
        'is_active',
        'location',
    )
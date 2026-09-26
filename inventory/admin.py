from django.contrib import admin
from .models import Category, Product, Stock


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'sku',
        'category',
        'unit_of_measure',
        'created_at'
    )

    search_fields = ('name', 'sku')

    list_filter = ('category',)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'location',
        'quantity',
        'updated_at'
    )

    search_fields = (
        'product__name',
        'product__sku',
        'location__name'
    )

    list_filter = ('location',)
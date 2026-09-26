from django.contrib import admin
from .models import Warehouse, Location


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'address',
        'created_at'
    )

    search_fields = ('name', 'address')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'warehouse',
        'created_at'
    )

    search_fields = (
        'name',
        'warehouse__name'
    )

    list_filter = ('warehouse',)
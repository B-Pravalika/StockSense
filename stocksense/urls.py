from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'accounts/',
        include('accounts.urls')
    ),

    path(
        'inventory/',
        include('inventory.urls')
    ),

    path(
        'warehouse/',
        include('warehouse.urls')
    ),

    path(
        'operations/',
        include('operations.urls')
    ),

    path(
        '',
        include('dashboard.urls')
    ),
]
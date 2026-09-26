from django.urls import path

from . import views


app_name = 'inventory'


urlpatterns = [

    path(
        'products/',
        views.product_list,
        name='product_list'
    ),

    path(
        'products/add/',
        views.product_create,
        name='product_create'
    ),

    path(
        'products/<int:pk>/edit/',
        views.product_update,
        name='product_update'
    ),

    path(
        'products/<int:pk>/delete/',
        views.product_delete,
        name='product_delete'
    ),

    path(
        'categories/',
        views.category_list,
        name='category_list'
    ),

    path(
        'categories/add/',
        views.category_create,
        name='category_create'
    ),

    path(
        'categories/<int:pk>/delete/',
        views.category_delete,
        name='category_delete'
    ),

path('stock/', views.stock_list, name='stock_list'),
path('stock/add/', views.stock_create, name='stock_create'),

]
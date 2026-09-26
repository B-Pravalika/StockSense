from django.urls import path

from . import views


app_name = 'warehouse'


urlpatterns = [

    path(
        '',
        views.warehouse_list,
        name='warehouse_list'
    ),

    path(
        'add/',
        views.warehouse_create,
        name='warehouse_create'
    ),

    path(
        '<int:pk>/edit/',
        views.warehouse_update,
        name='warehouse_update'
    ),

    path(
        '<int:pk>/delete/',
        views.warehouse_delete,
        name='warehouse_delete'
    ),

    path(
        'locations/',
        views.location_list,
        name='location_list'
    ),

    path(
        'locations/add/',
        views.location_create,
        name='location_create'
    ),

    path(
        'locations/<int:pk>/edit/',
        views.location_update,
        name='location_update'
    ),

    path(
        'locations/<int:pk>/delete/',
        views.location_delete,
        name='location_delete'
    ),

]
from django.urls import path

from . import views


app_name = 'operations'


urlpatterns = [

    # =========================
    # SUPPLIERS
    # =========================

    path(
        'suppliers/',
        views.supplier_list,
        name='supplier_list'
    ),

    path(
        'suppliers/add/',
        views.supplier_create,
        name='supplier_create'
    ),


    # =========================
    # RECEIPTS
    # =========================

    path(
        'receipts/',
        views.receipt_list,
        name='receipt_list'
    ),

    path(
        'receipts/add/',
        views.receipt_create,
        name='receipt_create'
    ),

    path(
        'receipts/<int:pk>/',
        views.receipt_detail,
        name='receipt_detail'
    ),

    path(
        'receipts/<int:pk>/add-item/',
        views.receipt_add_item,
        name='receipt_add_item'
    ),

    path(
        'receipts/<int:pk>/validate/',
        views.receipt_validate,
        name='receipt_validate'
    ),


    # =========================
    # DELIVERIES
    # =========================

    path(
        'deliveries/',
        views.delivery_list,
        name='delivery_list'
    ),

    path(
        'deliveries/add/',
        views.delivery_create,
        name='delivery_create'
    ),

    path(
        'deliveries/<int:pk>/',
        views.delivery_detail,
        name='delivery_detail'
    ),

    path(
        'deliveries/<int:pk>/add-item/',
        views.delivery_add_item,
        name='delivery_add_item'
    ),

    path(
        'deliveries/<int:pk>/validate/',
        views.delivery_validate,
        name='delivery_validate'
    ),


    # =========================
    # INTERNAL TRANSFERS
    # =========================

    path(
        'transfers/',
        views.transfer_list,
        name='transfer_list'
    ),

    path(
        'transfers/add/',
        views.transfer_create,
        name='transfer_create'
    ),

    path(
        'transfers/<int:pk>/',
        views.transfer_detail,
        name='transfer_detail'
    ),

    path(
        'transfers/<int:pk>/add-item/',
        views.transfer_add_item,
        name='transfer_add_item'
    ),

    path(
        'transfers/<int:pk>/validate/',
        views.transfer_validate,
        name='transfer_validate'
    ),


    # =========================
    # INVENTORY ADJUSTMENTS
    # =========================

    path(
        'adjustments/',
        views.adjustment_list,
        name='adjustment_list'
    ),

    path(
        'adjustments/add/',
        views.adjustment_create,
        name='adjustment_create'
    ),

    path(
        'adjustments/<int:pk>/',
        views.adjustment_detail,
        name='adjustment_detail'
    ),

    path(
        'adjustments/<int:pk>/add-item/',
        views.adjustment_add_item,
        name='adjustment_add_item'
    ),

    path(
        'adjustments/<int:pk>/validate/',
        views.adjustment_validate,
        name='adjustment_validate'
    ),

    path(
        'ledger/',
        views.ledger_list,
        name='ledger_list'
    ),

path(
    'reorder-rules/',
    views.reorder_rule_list,
    name='reorder_rule_list'
),

path(
    'reorder-rules/add/',
    views.reorder_rule_create,
    name='reorder_rule_create'
),

path(
    'reorder-rules/<int:pk>/edit/',
    views.reorder_rule_edit,
    name='reorder_rule_edit'
),

path(
    'reorder-rules/<int:pk>/delete/',
    views.reorder_rule_delete,
    name='reorder_rule_delete'
),

]
from django.db import transaction

from operations.models import (
    Receipt,
    Delivery,
    InternalTransfer,
    InventoryAdjustment,
)

from operations.services.stock_service import (
    increase_stock,
    decrease_stock,
    transfer_stock,
    adjust_stock,
)


@transaction.atomic
def validate_receipt(receipt):
    """
    Validate a receipt and increase stock for every receipt item.

    A receipt can only be validated when it is READY.
    After successful validation, its status becomes DONE.
    """

    if receipt.status != 'READY':
        raise ValueError(
            f"Receipt {receipt.reference} must be READY before validation."
        )

    items = receipt.items.all()

    if not items.exists():
        raise ValueError(
            f"Receipt {receipt.reference} has no items."
        )

    for item in items:
        increase_stock(
            product=item.product,
            location=receipt.destination,
            quantity=item.quantity,
            reference=receipt.reference,
            operation='RECEIPT',
            notes=f"Receipt from {receipt.supplier.name}"
        )

    receipt.status = 'DONE'
    receipt.save(update_fields=['status', 'updated_at'])

    return receipt


@transaction.atomic
def validate_delivery(delivery):
    """
    Validate a delivery and decrease stock for every delivery item.

    A delivery can only be validated when it is PACK.
    After successful validation, its status becomes DONE.
    """

    if delivery.status != 'PACK':
        raise ValueError(
            f"Delivery {delivery.reference} must be PACK before validation."
        )

    items = delivery.items.all()

    if not items.exists():
        raise ValueError(
            f"Delivery {delivery.reference} has no items."
        )

    for item in items:
        decrease_stock(
            product=item.product,
            location=delivery.source_location,
            quantity=item.quantity,
            reference=delivery.reference,
            operation='DELIVERY',
            notes=f"Delivery to {delivery.destination}"
        )

    delivery.status = 'DONE'
    delivery.save(update_fields=['status', 'updated_at'])

    return delivery


@transaction.atomic
def validate_transfer(transfer):
    """
    Validate an internal transfer.

    Stock is moved from the source location to the destination location.

    A transfer can only be validated when it is READY.
    """

    if transfer.status != 'READY':
        raise ValueError(
            f"Transfer {transfer.reference} must be READY before validation."
        )

    items = transfer.items.all()

    if not items.exists():
        raise ValueError(
            f"Transfer {transfer.reference} has no items."
        )

    for item in items:
        transfer_stock(
            product=item.product,
            source_location=transfer.source_location,
            destination_location=transfer.destination_location,
            quantity=item.quantity,
            reference=transfer.reference,
            notes="Internal stock transfer"
        )

    transfer.status = 'DONE'
    transfer.save(update_fields=['status', 'updated_at'])

    return transfer


@transaction.atomic
def validate_adjustment(adjustment):
    """
    Validate an inventory adjustment.

    The physical counted quantity becomes the new stock quantity.

    An adjustment can only be validated when it is DRAFT.
    """

    if adjustment.status != 'DRAFT':
        raise ValueError(
            f"Adjustment {adjustment.reference} must be DRAFT before validation."
        )

    items = adjustment.items.all()

    if not items.exists():
        raise ValueError(
            f"Adjustment {adjustment.reference} has no items."
        )

    for item in items:
        adjust_stock(
            product=item.product,
            location=adjustment.location,
            counted_quantity=item.counted_quantity,
            reference=adjustment.reference,
            notes=adjustment.reason
        )

    adjustment.status = 'DONE'
    adjustment.save(update_fields=['status', 'updated_at'])

    return adjustment
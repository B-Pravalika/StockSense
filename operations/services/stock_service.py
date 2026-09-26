from decimal import Decimal

from django.db import transaction

from inventory.models import Stock
from operations.models import (
    Delivery,
    InternalTransfer,
    InventoryAdjustment,
    Receipt,
    StockLedger,
)

@transaction.atomic
def increase_stock(product, location, quantity, reference, operation='RECEIPT', notes=''):
    """
    Increase stock at a specific location and create a ledger entry.
    """

    quantity = Decimal(str(quantity))

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    stock, created = Stock.objects.get_or_create(
        product=product,
        location=location,
        defaults={'quantity': Decimal('0')}
    )

    stock.quantity += quantity
    stock.save()

    StockLedger.objects.create(
        reference=reference,
        product=product,
        location=location,
        operation=operation,
        quantity=quantity,
        notes=notes
    )

    return stock


@transaction.atomic
def decrease_stock(product, location, quantity, reference, operation='DELIVERY', notes=''):
    """
    Decrease stock at a specific location and create a ledger entry.
    """

    quantity = Decimal(str(quantity))

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    stock = Stock.objects.select_for_update().filter(
        product=product,
        location=location
    ).first()

    if stock is None:
        raise ValueError(
            f"No stock record exists for {product.name} "
            f"at {location.name}."
        )

    if stock.quantity < quantity:
        raise ValueError(
            f"Insufficient stock for {product.name}. "
            f"Available: {stock.quantity}, "
            f"Requested: {quantity}."
        )

    stock.quantity -= quantity
    stock.save()

    StockLedger.objects.create(
        reference=reference,
        product=product,
        location=location,
        operation=operation,
        quantity=-quantity,
        notes=notes
    )

    return stock


@transaction.atomic
def transfer_stock(
    product,
    source_location,
    destination_location,
    quantity,
    reference,
    notes=''
):
    """
    Move stock from one location to another.
    """

    quantity = Decimal(str(quantity))

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    if source_location == destination_location:
        raise ValueError(
            "Source and destination locations must be different."
        )

    decrease_stock(
        product=product,
        location=source_location,
        quantity=quantity,
        reference=reference,
        operation='TRANSFER_OUT',
        notes=notes
    )

    increase_stock(
        product=product,
        location=destination_location,
        quantity=quantity,
        reference=reference,
        operation='TRANSFER_IN',
        notes=notes
    )

    return True


@transaction.atomic
def adjust_stock(
    product,
    location,
    counted_quantity,
    reference,
    notes=''
):
    """
    Adjust stock to match the physical counted quantity.
    """

    counted_quantity = Decimal(str(counted_quantity))

    if counted_quantity < 0:
        raise ValueError(
            "Counted quantity cannot be negative."
        )

    stock, created = Stock.objects.get_or_create(
        product=product,
        location=location,
        defaults={'quantity': Decimal('0')}
    )

    difference = counted_quantity - stock.quantity

    if difference == 0:
        return stock

    stock.quantity = counted_quantity
    stock.save()

    StockLedger.objects.create(
        reference=reference,
        product=product,
        location=location,
        operation='ADJUSTMENT',
        quantity=difference,
        notes=notes
    )

    return stock

@transaction.atomic
def process_receipt(receipt):

    receipt = Receipt.objects.select_for_update().get(
        pk=receipt.pk
    )

    if receipt.status == 'DONE':
        raise ValueError(
            f'Receipt {receipt.reference} has already been validated.'
        )

    if receipt.status == 'CANCELED':
        raise ValueError(
            f'Receipt {receipt.reference} is canceled and cannot be validated.'
        )

    items = list(
        receipt.items.select_related('product')
    )

    if not items:
        raise ValueError(
            'A receipt must contain at least one product.'
        )

    for item in items:

        increase_stock(
            product=item.product,
            location=receipt.destination,
            quantity=item.quantity,
            reference=receipt.reference,
            operation='RECEIPT',
            notes=f'Receipt from {receipt.supplier.name}.'
        )

    receipt.status = 'DONE'

    receipt.save(
        update_fields=[
            'status',
            'updated_at',
        ]
    )

    return receipt

@transaction.atomic
def process_delivery(delivery):
    """
    Validate a delivery and decrease stock
    for every delivery item.
    """

    delivery = Delivery.objects.select_for_update().get(
        pk=delivery.pk
    )

    if delivery.status == 'DONE':
        raise ValueError(
            f'Delivery {delivery.reference} has already been validated.'
        )

    if delivery.status == 'CANCELED':
        raise ValueError(
            f'Delivery {delivery.reference} is canceled '
            f'and cannot be validated.'
        )

    items = list(
        delivery.items.select_related('product')
    )

    if not items:
        raise ValueError(
            'A delivery must contain at least one product.'
        )

    # First check ALL stock before changing anything.
    for item in items:

        stock = Stock.objects.filter(
            product=item.product,
            location=delivery.source_location
        ).first()

        if stock is None:
            raise ValueError(
                f'No stock exists for {item.product.name} '
                f'at {delivery.source_location.name}.'
            )

        if stock.quantity < item.quantity:
            raise ValueError(
                f'Insufficient stock for {item.product.name}. '
                f'Available: {stock.quantity}, '
                f'Requested: {item.quantity}.'
            )

    # Only after all checks pass, decrease stock.
    for item in items:

        decrease_stock(
            product=item.product,
            location=delivery.source_location,
            quantity=item.quantity,
            reference=delivery.reference,
            operation='DELIVERY',
            notes=f'Delivery to {delivery.destination}.'
        )

    delivery.status = 'DONE'

    delivery.save(
        update_fields=[
            'status',
            'updated_at',
        ]
    )

    return delivery

@transaction.atomic
def process_transfer(transfer):
    """
    Validate an internal transfer and move stock
    from the source location to the destination location.
    """

    transfer = InternalTransfer.objects.select_for_update().get(
        pk=transfer.pk
    )

    if transfer.status == 'DONE':
        raise ValueError(
            f'Transfer {transfer.reference} has already been validated.'
        )

    if transfer.status == 'CANCELED':
        raise ValueError(
            f'Transfer {transfer.reference} is canceled '
            f'and cannot be validated.'
        )

    if transfer.source_location == transfer.destination_location:
        raise ValueError(
            'Source and destination locations must be different.'
        )

    items = list(
        transfer.items.select_related('product')
    )

    if not items:
        raise ValueError(
            'A transfer must contain at least one product.'
        )

    # Check ALL source stock before changing anything.
    for item in items:

        stock = Stock.objects.filter(
            product=item.product,
            location=transfer.source_location
        ).first()

        if stock is None:
            raise ValueError(
                f'No stock exists for {item.product.name} '
                f'at {transfer.source_location.name}.'
            )

        if stock.quantity < item.quantity:
            raise ValueError(
                f'Insufficient stock for {item.product.name}. '
                f'Available: {stock.quantity}, '
                f'Requested: {item.quantity}.'
            )

    # Move every item.
    for item in items:

        transfer_stock(
            product=item.product,
            source_location=transfer.source_location,
            destination_location=transfer.destination_location,
            quantity=item.quantity,
            reference=transfer.reference,
            notes=(
                f'Transfer from '
                f'{transfer.source_location.name} to '
                f'{transfer.destination_location.name}.'
            )
        )

    transfer.status = 'DONE'

    transfer.save(
        update_fields=[
            'status',
            'updated_at',
        ]
    )

    return transfer

@transaction.atomic
def process_adjustment(adjustment):

    adjustment = InventoryAdjustment.objects.select_for_update().get(
        pk=adjustment.pk
    )

    if adjustment.status == 'DONE':
        raise ValueError(
            f'Adjustment {adjustment.reference} '
            f'has already been completed.'
        )

    if adjustment.status == 'CANCELED':
        raise ValueError(
            f'Adjustment {adjustment.reference} '
            f'is canceled and cannot be completed.'
        )

    items = list(
        adjustment.items.select_related('product')
    )

    if not items:
        raise ValueError(
            'An adjustment must contain at least one product.'
        )

    for item in items:

        if item.counted_quantity < 0:
            raise ValueError(
                f'Counted quantity for {item.product.name} '
                f'cannot be negative.'
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

    adjustment.save(
        update_fields=[
            'status',
            'updated_at',
        ]
    )

    return adjustment
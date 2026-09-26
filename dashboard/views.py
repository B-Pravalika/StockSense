from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from inventory.models import Stock
from operations.models import (
    Delivery,
    InternalTransfer,
    Receipt,
    ReorderRule,
    StockLedger,
)


@login_required
def home(request):
    # Total quantity currently available across all locations
    total_stock = (
        Stock.objects.aggregate(
            total=Sum('quantity')
        )['total'] or 0
    )

    # ---------------------------------------------------------
    # Pending operations
    # ---------------------------------------------------------

    pending_receipts = Receipt.objects.filter(
        status__in=['DRAFT', 'WAITING', 'READY']
    ).count()

    pending_deliveries = Delivery.objects.filter(
        status__in=[
            'DRAFT',
            'WAITING',
            'READY',
            'PICK',
            'PACK',
        ]
    ).count()

    pending_transfers = InternalTransfer.objects.filter(
        status__in=[
            'DRAFT',
            'WAITING',
            'READY',
        ]
    ).count()

    # ---------------------------------------------------------
    # Low-stock items
    #
    # Only active reorder rules are considered.
    # A product is low-stock when:
    #
    # current stock < configured minimum quantity
    # ---------------------------------------------------------

    reorder_rules = ReorderRule.objects.select_related(
        'product',
        'location',
        'location__warehouse',
    ).filter(
        is_active=True
    )

    low_stock_items = []

    for rule in reorder_rules:
        stock = Stock.objects.filter(
            product=rule.product,
            location=rule.location,
        ).first()

        current_quantity = stock.quantity if stock else 0

        if current_quantity < rule.minimum_quantity:
            low_stock_items.append({
                'product': rule.product,
                'location': rule.location,
                'warehouse': rule.location.warehouse,
                'current_quantity': current_quantity,
                'minimum_quantity': rule.minimum_quantity,
                'reorder_quantity': rule.reorder_quantity,
                'maximum_quantity': rule.maximum_quantity,
            })

    # Lowest quantity first
    low_stock_items.sort(
        key=lambda item: item['current_quantity']
    )

    # Dashboard KPI
    low_stock_count = len(low_stock_items)

    # Out-of-stock items from configured reorder rules
    out_of_stock_count = sum(
        1
        for item in low_stock_items
        if item['current_quantity'] == 0
    )

    # Display maximum 10 low-stock items
    low_stock_items = low_stock_items[:10]

    # ---------------------------------------------------------
    # Recent stock movements
    # ---------------------------------------------------------

    recent_movements = StockLedger.objects.select_related(
        'product',
        'location',
        'location__warehouse',
    ).order_by(
        '-created_at'
    )[:10]

    # ---------------------------------------------------------
    # Stock grouped by warehouse
    # ---------------------------------------------------------

    warehouse_stock = (
        Stock.objects
        .values('location__warehouse__name')
        .annotate(
            total_quantity=Sum('quantity')
        )
        .order_by('-total_quantity')
    )

    context = {
        'total_stock': total_stock,

        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,

        'pending_receipts': pending_receipts,
        'pending_deliveries': pending_deliveries,
        'pending_transfers': pending_transfers,

        'recent_movements': recent_movements,
        'low_stock_items': low_stock_items,
        'warehouse_stock': warehouse_stock,
    }

    return render(
        request,
        'dashboard/home.html',
        context
    )
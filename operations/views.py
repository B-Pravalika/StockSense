from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from warehouse.models import Location, Warehouse

from .forms import (
    AdjustmentItemForm,
    DeliveryForm,
    DeliveryItemForm,
    InternalTransferForm,
    InventoryAdjustmentForm,
    ReceiptForm,
    ReceiptItemForm,
    SupplierForm,
    TransferItemForm,
    ReorderRuleForm
)

from .models import (
    Delivery,
    DeliveryItem,
    InternalTransfer,
    InventoryAdjustment,
    AdjustmentItem,
    Receipt,
    ReceiptItem,
    ReorderRule,
    StockLedger,
    Supplier,
    TransferItem,
)

from .services.stock_service import (
    process_adjustment,
    process_delivery,
    process_receipt,
    process_transfer,
)

@login_required
def supplier_list(request):

    suppliers = Supplier.objects.order_by('name')

    return render(
        request,
        'operations/supplier_list.html',
        {
            'suppliers': suppliers,
        }
    )


@login_required
def supplier_create(request):

    if request.method == 'POST':

        form = SupplierForm(request.POST)

        if form.is_valid():

            supplier = form.save()

            messages.success(
                request,
                f'Supplier "{supplier.name}" was created successfully.'
            )

            return redirect('operations:supplier_list')

    else:

        form = SupplierForm()

    return render(
        request,
        'operations/supplier_form.html',
        {
            'form': form,
            'page_title': 'Add Supplier',
            'button_text': 'Create Supplier',
        }
    )


@login_required
def receipt_list(request):
    receipts = Receipt.objects.select_related(
        'supplier',
        'destination',
        'destination__warehouse',
    ).prefetch_related(
        'items__product',
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    warehouse = request.GET.get('warehouse', '').strip()
    location = request.GET.get('location', '').strip()

    if search:
        receipts = receipts.filter(
            Q(reference__icontains=search)
            | Q(supplier__name__icontains=search)
            | Q(items__product__name__icontains=search)
            | Q(items__product__sku__icontains=search)
        ).distinct()

    if status:
        receipts = receipts.filter(status=status)

    if warehouse:
        receipts = receipts.filter(
            destination__warehouse_id=warehouse
        )

    if location:
        receipts = receipts.filter(
            destination_id=location
        )

    context = {
        'receipts': receipts,
        'search': search,
        'selected_status': status,
        'selected_warehouse': warehouse,
        'selected_location': location,
        'warehouses': Warehouse.objects.all().order_by('name'),
        'locations': Location.objects.select_related(
            'warehouse'
        ).order_by(
            'warehouse__name',
            'name'
        ),
    }

    return render(
        request,
        'operations/receipt_list.html',
        context
    )

@login_required
def receipt_create(request):

    if request.method == 'POST':

        form = ReceiptForm(request.POST)

        if form.is_valid():

            receipt = form.save()

            messages.success(
                request,
                f'Receipt "{receipt.reference}" was created successfully.'
            )

            return redirect(
                'operations:receipt_detail',
                pk=receipt.pk
            )

    else:

        form = ReceiptForm()

    return render(
        request,
        'operations/receipt_form.html',
        {
            'form': form,
            'page_title': 'Create Receipt',
            'button_text': 'Create Receipt',
        }
    )


@login_required
def receipt_detail(request, pk):

    receipt = get_object_or_404(
        Receipt.objects.select_related(
            'supplier',
            'destination',
        ).prefetch_related(
            'items__product'
        ),
        pk=pk
    )

    item_form = ReceiptItemForm()

    return render(
        request,
        'operations/receipt_detail.html',
        {
            'receipt': receipt,
            'item_form': item_form,
        }
    )


@login_required
def receipt_add_item(request, pk):

    receipt = get_object_or_404(
        Receipt,
        pk=pk
    )

    if receipt.status != 'DRAFT':

        messages.error(
            request,
            'Products can only be added while the receipt is in Draft status.'
        )

        return redirect(
            'operations:receipt_detail',
            pk=receipt.pk
        )

    if request.method == 'POST':

        form = ReceiptItemForm(request.POST)

        if form.is_valid():

            item = form.save(commit=False)
            item.receipt = receipt
            item.save()

            messages.success(
                request,
                f'"{item.product.name}" was added to the receipt.'
            )

    return redirect(
        'operations:receipt_detail',
        pk=receipt.pk
    )


@login_required
def receipt_validate(request, pk):

    receipt = get_object_or_404(
        Receipt,
        pk=pk
    )

    if request.method != 'POST':

        return redirect(
            'operations:receipt_detail',
            pk=receipt.pk
        )

    try:

        process_receipt(receipt)

        messages.success(
            request,
            f'Receipt "{receipt.reference}" was validated successfully. '
            f'Stock has been updated.'
        )

    except ValueError as error:

        messages.error(
            request,
            str(error)
        )

    return redirect(
        'operations:receipt_detail',
        pk=receipt.pk
    )

@login_required
def delivery_list(request):

    deliveries = Delivery.objects.select_related(
        'source_location',
        'source_location__warehouse',
    ).prefetch_related(
        'items'
    ).order_by('-created_at')

    return render(
        request,
        'operations/delivery_list.html',
        {
            'deliveries': deliveries,
        }
    )


@login_required
def delivery_create(request):

    if request.method == 'POST':

        form = DeliveryForm(request.POST)

        if form.is_valid():

            delivery = form.save()

            messages.success(
                request,
                f'Delivery "{delivery.reference}" was created successfully.'
            )

            return redirect(
                'operations:delivery_detail',
                pk=delivery.pk
            )

    else:

        form = DeliveryForm()

    return render(
        request,
        'operations/delivery_form.html',
        {
            'form': form,
            'page_title': 'Create Delivery Order',
            'button_text': 'Create Delivery',
        }
    )


@login_required
def delivery_detail(request, pk):

    delivery = get_object_or_404(
        Delivery.objects.select_related(
            'source_location',
            'source_location__warehouse',
        ).prefetch_related(
            'items__product'
        ),
        pk=pk
    )

    item_form = DeliveryItemForm()

    return render(
        request,
        'operations/delivery_detail.html',
        {
            'delivery': delivery,
            'item_form': item_form,
        }
    )


@login_required
def delivery_add_item(request, pk):

    delivery = get_object_or_404(
        Delivery,
        pk=pk
    )

    if delivery.status != 'DRAFT':

        messages.error(
            request,
            'Products can only be added while the delivery '
            'is in Draft status.'
        )

        return redirect(
            'operations:delivery_detail',
            pk=delivery.pk
        )

    if request.method == 'POST':

        form = DeliveryItemForm(request.POST)

        if form.is_valid():

            item = form.save(commit=False)
            item.delivery = delivery
            item.save()

            messages.success(
                request,
                f'"{item.product.name}" was added to the delivery.'
            )

    return redirect(
        'operations:delivery_detail',
        pk=delivery.pk
    )


@login_required
def delivery_validate(request, pk):

    delivery = get_object_or_404(
        Delivery,
        pk=pk
    )

    if request.method != 'POST':

        return redirect(
            'operations:delivery_detail',
            pk=delivery.pk
        )

    try:

        process_delivery(delivery)

        messages.success(
            request,
            f'Delivery "{delivery.reference}" was validated successfully. '
            f'Stock has been updated.'
        )

    except ValueError as error:

        messages.error(
            request,
            str(error)
        )

    return redirect(
        'operations:delivery_detail',
        pk=delivery.pk
    )

@login_required
def transfer_list(request):

    transfers = InternalTransfer.objects.select_related(
        'source_location',
        'source_location__warehouse',
        'destination_location',
        'destination_location__warehouse',
    ).prefetch_related(
        'items'
    ).order_by('-created_at')

    return render(
        request,
        'operations/transfer_list.html',
        {
            'transfers': transfers,
        }
    )


@login_required
def transfer_create(request):

    if request.method == 'POST':

        form = InternalTransferForm(request.POST)

        if form.is_valid():

            transfer = form.save()

            messages.success(
                request,
                f'Transfer "{transfer.reference}" was created successfully.'
            )

            return redirect(
                'operations:transfer_detail',
                pk=transfer.pk
            )

    else:

        form = InternalTransferForm()

    return render(
        request,
        'operations/transfer_form.html',
        {
            'form': form,
            'page_title': 'Create Internal Transfer',
            'button_text': 'Create Transfer',
        }
    )


@login_required
def transfer_detail(request, pk):

    transfer = get_object_or_404(
        InternalTransfer.objects.select_related(
            'source_location',
            'source_location__warehouse',
            'destination_location',
            'destination_location__warehouse',
        ).prefetch_related(
            'items__product'
        ),
        pk=pk
    )

    item_form = TransferItemForm()

    return render(
        request,
        'operations/transfer_detail.html',
        {
            'transfer': transfer,
            'item_form': item_form,
        }
    )


@login_required
def transfer_add_item(request, pk):

    transfer = get_object_or_404(
        InternalTransfer,
        pk=pk
    )

    if transfer.status != 'DRAFT':

        messages.error(
            request,
            'Products can only be added while the transfer '
            'is in Draft status.'
        )

        return redirect(
            'operations:transfer_detail',
            pk=transfer.pk
        )

    if request.method == 'POST':

        form = TransferItemForm(request.POST)

        if form.is_valid():

            item = form.save(commit=False)
            item.transfer = transfer
            item.save()

            messages.success(
                request,
                f'"{item.product.name}" was added to the transfer.'
            )

    return redirect(
        'operations:transfer_detail',
        pk=transfer.pk
    )


@login_required
def transfer_validate(request, pk):

    transfer = get_object_or_404(
        InternalTransfer,
        pk=pk
    )

    if request.method != 'POST':

        return redirect(
            'operations:transfer_detail',
            pk=transfer.pk
        )

    try:

        process_transfer(transfer)

        messages.success(
            request,
            f'Transfer "{transfer.reference}" was validated successfully. '
            f'Stock has been moved.'
        )

    except ValueError as error:

        messages.error(
            request,
            str(error)
        )

    return redirect(
        'operations:transfer_detail',
        pk=transfer.pk
    )

@login_required
def adjustment_list(request):

    adjustments = InventoryAdjustment.objects.select_related(
        'location',
        'location__warehouse',
    ).prefetch_related(
        'items'
    ).order_by('-created_at')

    return render(
        request,
        'operations/adjustment_list.html',
        {
            'adjustments': adjustments,
        }
    )


@login_required
def adjustment_create(request):

    if request.method == 'POST':

        form = InventoryAdjustmentForm(request.POST)

        if form.is_valid():

            adjustment = form.save()

            messages.success(
                request,
                f'Adjustment "{adjustment.reference}" '
                f'was created successfully.'
            )

            return redirect(
                'operations:adjustment_detail',
                pk=adjustment.pk
            )

    else:

        form = InventoryAdjustmentForm()

    return render(
        request,
        'operations/adjustment_form.html',
        {
            'form': form,
            'page_title': 'Create Inventory Adjustment',
            'button_text': 'Create Adjustment',
        }
    )


@login_required
def adjustment_detail(request, pk):

    adjustment = get_object_or_404(
        InventoryAdjustment.objects.select_related(
            'location',
            'location__warehouse',
        ).prefetch_related(
            'items__product'
        ),
        pk=pk
    )

    item_form = AdjustmentItemForm()

    return render(
        request,
        'operations/adjustment_detail.html',
        {
            'adjustment': adjustment,
            'item_form': item_form,
        }
    )


@login_required
def adjustment_add_item(request, pk):

    adjustment = get_object_or_404(
        InventoryAdjustment,
        pk=pk
    )

    if adjustment.status != 'DRAFT':

        messages.error(
            request,
            'Products can only be added while the adjustment '
            'is in Draft status.'
        )

        return redirect(
            'operations:adjustment_detail',
            pk=adjustment.pk
        )

    if request.method == 'POST':

        form = AdjustmentItemForm(request.POST)

        if form.is_valid():

            item = form.save(commit=False)

            item.adjustment = adjustment

            item.save()

            messages.success(
                request,
                f'"{item.product.name}" was added to the adjustment.'
            )

    return redirect(
        'operations:adjustment_detail',
        pk=adjustment.pk
    )


@login_required
def adjustment_validate(request, pk):

    adjustment = get_object_or_404(
        InventoryAdjustment,
        pk=pk
    )

    if request.method != 'POST':

        return redirect(
            'operations:adjustment_detail',
            pk=adjustment.pk
        )

    try:

        process_adjustment(adjustment)

        messages.success(
            request,
            f'Adjustment "{adjustment.reference}" '
            f'was completed successfully. '
            f'Stock has been updated.'
        )

    except ValueError as error:

        messages.error(
            request,
            str(error)
        )

    return redirect(
        'operations:adjustment_detail',
        pk=adjustment.pk
    )

@login_required
def ledger_list(request):

    ledger_entries = StockLedger.objects.select_related(
        'product',
        'location',
        'location__warehouse',
    ).order_by('-created_at')

    return render(
        request,
        'operations/ledger_list.html',
        {
            'ledger_entries': ledger_entries,
        }
    )

@login_required
def reorder_rule_list(request):
    rules = ReorderRule.objects.select_related(
        'product',
        'location',
        'location__warehouse',
    ).order_by(
        'product__name',
        'location__warehouse__name',
        'location__name',
    )

    return render(
        request,
        'operations/reorder_rule_list.html',
        {
            'rules': rules,
        }
    )


@login_required
def reorder_rule_create(request):
    if request.method == 'POST':
        form = ReorderRuleForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('operations:reorder_rule_list')

    else:
        form = ReorderRuleForm()

    return render(
        request,
        'operations/reorder_rule_form.html',
        {
            'form': form,
            'title': 'Add Reorder Rule',
        }
    )


@login_required
def reorder_rule_edit(request, pk):
    rule = get_object_or_404(ReorderRule, pk=pk)

    if request.method == 'POST':
        form = ReorderRuleForm(
            request.POST,
            instance=rule
        )

        if form.is_valid():
            form.save()
            return redirect('operations:reorder_rule_list')

    else:
        form = ReorderRuleForm(instance=rule)

    return render(
        request,
        'operations/reorder_rule_form.html',
        {
            'form': form,
            'title': 'Edit Reorder Rule',
        }
    )


@login_required
def reorder_rule_delete(request, pk):
    rule = get_object_or_404(ReorderRule, pk=pk)

    if request.method == 'POST':
        rule.delete()
        return redirect('operations:reorder_rule_list')

    return render(
        request,
        'operations/reorder_rule_confirm_delete.html',
        {
            'rule': rule,
        }
    )
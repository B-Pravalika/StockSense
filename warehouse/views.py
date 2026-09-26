from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LocationForm, WarehouseForm
from .models import Location, Warehouse


@login_required
def warehouse_list(request):

    warehouses = Warehouse.objects.prefetch_related(
        'locations'
    ).order_by('name')

    return render(
        request,
        'warehouse/warehouse_list.html',
        {
            'warehouses': warehouses,
        }
    )


@login_required
def warehouse_create(request):

    if request.method == 'POST':

        form = WarehouseForm(request.POST)

        if form.is_valid():

            warehouse = form.save()

            messages.success(
                request,
                f'Warehouse "{warehouse.name}" was created successfully.'
            )

            return redirect('warehouse:warehouse_list')

    else:
        form = WarehouseForm()

    return render(
        request,
        'warehouse/warehouse_form.html',
        {
            'form': form,
            'page_title': 'Add Warehouse',
            'button_text': 'Create Warehouse',
        }
    )


@login_required
def warehouse_update(request, pk):

    warehouse = get_object_or_404(
        Warehouse,
        pk=pk
    )

    if request.method == 'POST':

        form = WarehouseForm(
            request.POST,
            instance=warehouse
        )

        if form.is_valid():

            warehouse = form.save()

            messages.success(
                request,
                f'Warehouse "{warehouse.name}" was updated successfully.'
            )

            return redirect('warehouse:warehouse_list')

    else:

        form = WarehouseForm(
            instance=warehouse
        )

    return render(
        request,
        'warehouse/warehouse_form.html',
        {
            'form': form,
            'warehouse': warehouse,
            'page_title': 'Edit Warehouse',
            'button_text': 'Update Warehouse',
        }
    )


@login_required
def warehouse_delete(request, pk):

    warehouse = get_object_or_404(
        Warehouse,
        pk=pk
    )

    if request.method == 'POST':

        warehouse_name = warehouse.name

        warehouse.delete()

        messages.success(
            request,
            f'Warehouse "{warehouse_name}" was deleted successfully.'
        )

        return redirect('warehouse:warehouse_list')

    return render(
        request,
        'warehouse/warehouse_confirm_delete.html',
        {
            'warehouse': warehouse,
        }
    )


@login_required
def location_list(request):

    locations = Location.objects.select_related(
        'warehouse'
    ).order_by(
        'warehouse__name',
        'name'
    )

    return render(
        request,
        'warehouse/location_list.html',
        {
            'locations': locations,
        }
    )


@login_required
def location_create(request):

    if request.method == 'POST':

        form = LocationForm(request.POST)

        if form.is_valid():

            location = form.save()

            messages.success(
                request,
                f'Location "{location.name}" was created successfully.'
            )

            return redirect('warehouse:location_list')

    else:

        form = LocationForm()

    return render(
        request,
        'warehouse/location_form.html',
        {
            'form': form,
            'page_title': 'Add Location',
            'button_text': 'Create Location',
        }
    )


@login_required
def location_update(request, pk):

    location = get_object_or_404(
        Location,
        pk=pk
    )

    if request.method == 'POST':

        form = LocationForm(
            request.POST,
            instance=location
        )

        if form.is_valid():

            location = form.save()

            messages.success(
                request,
                f'Location "{location.name}" was updated successfully.'
            )

            return redirect('warehouse:location_list')

    else:

        form = LocationForm(
            instance=location
        )

    return render(
        request,
        'warehouse/location_form.html',
        {
            'form': form,
            'location': location,
            'page_title': 'Edit Location',
            'button_text': 'Update Location',
        }
    )


@login_required
def location_delete(request, pk):

    location = get_object_or_404(
        Location,
        pk=pk
    )

    if request.method == 'POST':

        location_name = location.name

        location.delete()

        messages.success(
            request,
            f'Location "{location_name}" was deleted successfully.'
        )

        return redirect('warehouse:location_list')

    return render(
        request,
        'warehouse/location_confirm_delete.html',
        {
            'location': location,
        }
    )
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm, CategoryForm, StockForm
from .models import Category, Product, Stock

from operations.services.stock_service import adjust_stock

@login_required
def product_list(request):

    search = request.GET.get('search', '').strip()

    products = Product.objects.select_related(
        'category'
    ).order_by('name')

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search) |
            Q(category__name__icontains=search)
        )

    context = {
        'products': products,
        'search': search,
    }

    return render(
        request,
        'inventory/product_list.html',
        context
    )


@login_required
def product_create(request):

    if request.method == 'POST':

        form = ProductForm(request.POST)

        if form.is_valid():

            product = form.save()

            messages.success(
                request,
                f'Product "{product.name}" was created successfully.'
            )

            return redirect('inventory:product_list')

    else:
        form = ProductForm()

    return render(
        request,
        'inventory/product_form.html',
        {
            'form': form,
            'page_title': 'Add Product',
            'button_text': 'Create Product',
        }
    )


@login_required
def product_update(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            instance=product
        )

        if form.is_valid():

            product = form.save()

            messages.success(
                request,
                f'Product "{product.name}" was updated successfully.'
            )

            return redirect('inventory:product_list')

    else:
        form = ProductForm(
            instance=product
        )

    return render(
        request,
        'inventory/product_form.html',
        {
            'form': form,
            'page_title': 'Edit Product',
            'button_text': 'Update Product',
            'product': product,
        }
    )


@login_required
def product_delete(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if request.method == 'POST':

        product_name = product.name

        product.delete()

        messages.success(
            request,
            f'Product "{product_name}" was deleted successfully.'
        )

        return redirect('inventory:product_list')

    return render(
        request,
        'inventory/product_confirm_delete.html',
        {
            'product': product,
        }
    )


@login_required
def category_list(request):

    categories = Category.objects.order_by('name')

    return render(
        request,
        'inventory/category_list.html',
        {
            'categories': categories,
        }
    )


@login_required
def category_create(request):

    if request.method == 'POST':

        form = CategoryForm(request.POST)

        if form.is_valid():

            category = form.save()

            messages.success(
                request,
                f'Category "{category.name}" was created successfully.'
            )

            return redirect('inventory:category_list')

    else:
        form = CategoryForm()

    return render(
        request,
        'inventory/category_form.html',
        {
            'form': form,
            'page_title': 'Add Category',
            'button_text': 'Create Category',
        }
    )


@login_required
def category_delete(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == 'POST':

        category_name = category.name

        category.delete()

        messages.success(
            request,
            f'Category "{category_name}" was deleted successfully.'
        )

        return redirect('inventory:category_list')

    return render(
        request,
        'inventory/category_confirm_delete.html',
        {
            'category': category,
        }
    )

@login_required
def stock_list(request):

    stocks = Stock.objects.select_related(
        'product',
        'product__category',
        'location',
        'location__warehouse'
    ).order_by(
        'product__name',
        'location__warehouse__name',
        'location__name'
    )

    return render(
        request,
        'inventory/stock_list.html',
        {
            'stocks': stocks,
        }
    )


@login_required
def stock_create(request):

    if request.method == 'POST':

        form = StockForm(request.POST)

        if form.is_valid():

            product = form.cleaned_data['product']
            location = form.cleaned_data['location']
            quantity = form.cleaned_data['quantity']

            try:

                stock = Stock.objects.filter(
                    product=product,
                    location=location
                ).first()

                current_quantity = (
                    stock.quantity
                    if stock
                    else 0
                )

                if quantity < current_quantity:
                    raise ValueError(
                        'For reducing stock, use Inventory Adjustment '
                        'or Delivery instead of this screen.'
                    )

                difference = quantity - current_quantity

                if difference > 0:

                    adjust_stock(
                        product=product,
                        location=location,
                        counted_quantity=quantity,
                        reference='Initial Stock Entry',
                        notes='Stock created/updated from stock management.'
                    )

                elif stock is None:

                    adjust_stock(
                        product=product,
                        location=location,
                        counted_quantity=quantity,
                        reference='Initial Stock Entry',
                        notes='Initial stock entry.'
                    )

                messages.success(
                    request,
                    f'Stock for "{product.name}" at '
                    f'"{location.name}" was saved successfully.'
                )

                return redirect('inventory:stock_list')

            except ValueError as error:

                form.add_error(
                    'quantity',
                    str(error)
                )

    else:

        form = StockForm()

    return render(
        request,
        'inventory/stock_form.html',
        {
            'form': form,
            'page_title': 'Add Stock',
            'button_text': 'Save Stock',
        }
    )
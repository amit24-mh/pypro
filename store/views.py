from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem, Order, OrderItem
from .forms import CheckoutForm


# List products
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


# Product details
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/product_detail.html', {'product': product})


# View cart
@login_required
def view_cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in items)
    return render(request, 'store/cart.html', {'items': items, 'total': total})


# Add to cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')


# Checkout
@login_required
def checkout(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in items)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                total_amount=total
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            items.delete()  # clear cart
            return redirect('order_list')
    else:
        form = CheckoutForm()

    return render(request, 'store/checkout.html', {'form': form, 'total': total})


# Order list
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/orders.html', {'orders': orders})
# Home page view
def home(request):
    # Redirect to product list or show some featured products
    products = Product.objects.all()  # or filter for featured products
    return render(request, 'store/home.html', {'products': products})


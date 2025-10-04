from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem, Order, OrderItem
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product, CartItem, Order, OrderItem, Profile

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def create_superuser_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            messages.success(request, f"Superuser '{username}' created successfully!")

    return render(request, 'store/create_superuser.html')

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse

def user_login(request):
    if request.user.is_authenticated:
        return redirect('redirect_user')  # use this new function

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('redirect_user')  # redirect based on role
        else:
            return render(request, 'store/login.html', {'error': 'Invalid credentials'})
    return render(request, 'store/login.html')

# Home / Product list
@login_required
def home(request):
    query = request.GET.get('q')
    if query:
        # search by name, features, or description
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(features__icontains=query) | 
            Q(description__icontains=query)
        )
    else:
        products = Product.objects.all()
    
    return render(request, 'store/home.html', {
        'products': products,
        'query': query
    })

from django.contrib.auth import logout  # make sure this import is at the top

# Logout view
def user_logout(request):
    logout(request)
    return redirect('login')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/product_detail.html', {'product': product})

# Cart views
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def redirect_user(request):
    try:
        role = request.user.profile.role
    except Profile.DoesNotExist:
        # Create a profile if missing
        Profile.objects.create(user=request.user)
        role = request.user.profile.role

    if role == 'seller':
        return redirect('seller_dashboard')
    else:
        return redirect('home')


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

# Orders
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/orders.html', {'orders': orders})

# Checkout
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal for item in cart_items)
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            address=address,
            phone=phone,
            total_amount=total
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        cart_items.delete()
        return redirect('order_list')

    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})
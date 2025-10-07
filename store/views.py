from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product, CartItem, Order, OrderItem, Profile, Review, Wishlist

# Signals to create user profile automatically
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# -----------------------
# Superuser creation view
# -----------------------
def create_superuser_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
        else:
            user = User.objects.create_superuser(username=username, email=email, password=password)
            Profile.objects.get_or_create(user=user, defaults={'role': 'seller'})
            messages.success(request, f"Superuser '{username}' created successfully!")
            return redirect('seller_dashboard')
    return render(request, 'store/create_superuser.html')

# -----------------------
# Authentication
# -----------------------
from django.contrib.auth import authenticate, login, logout

def user_login(request):
    if request.user.is_authenticated:
        return redirect('redirect_user')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect('login')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            Profile.objects.get_or_create(user=user)
            return redirect('redirect_user')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')
    return render(request, 'store/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def redirect_user(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if profile.role == 'seller':
        return redirect('seller_dashboard')
    else:
        return redirect('home')

# -----------------------
# Product views
# -----------------------
@login_required
def home(request):
    query = request.GET.get('q')
    products = Product.objects.all()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(features__icontains=query) |
            Q(description__icontains=query)
        )
    return render(request, 'store/home.html', {'products': products, 'query': query})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    recommendations = Product.objects.exclude(id=product.id)[:4]

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'recommendations': recommendations
    })

# -----------------------
# Reviews
# -----------------------
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        review, created = Review.objects.get_or_create(user=request.user, product=product)
        review.rating = rating
        review.comment = comment
        review.save()
        messages.success(request, "Review added successfully!")
    return redirect('product_detail', slug=product.slug)

# -----------------------
# Cart & Checkout
# -----------------------
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} added to cart")
    return redirect('view_cart')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart")
    return redirect('view_cart')

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
        messages.success(request, "Order placed successfully!")
        return redirect('order_list')
    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/orders.html', {'orders': orders})

# -----------------------
# Wishlist
# -----------------------
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"{product.name} added to wishlist")
    return redirect('product_detail', slug=product.slug)

@login_required
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, wishlist_id):
    item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    item.delete()
    messages.success(request, "Item removed from wishlist")
    return redirect('view_wishlist')

# -----------------------
# Seller dashboard
# -----------------------
@login_required
def seller_dashboard(request):
    return render(request, 'store/seller_dashboard.html')

from django.contrib.auth.models import User
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully!")
            return redirect('login')
    return render(request, 'store/signup.html')
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully!")
            return redirect('login')
    return render(request, 'store/signup.html')

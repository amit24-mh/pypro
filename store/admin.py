from django.contrib import admin
from .models import Category, Product, CartItem, Order, OrderItem, Review, Wishlist, Profile

# -----------------------------
# Category admin
# -----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

# -----------------------------
# Product admin
# -----------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# -----------------------------
# CartItem admin
# -----------------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    list_filter = ('user',)
    search_fields = ('product__name', 'user__username')

# -----------------------------
# Order admin
# -----------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'total_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'full_name', 'phone')

# -----------------------------
# OrderItem admin
# -----------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('product',)
    search_fields = ('product__name', 'order__user__username')

# -----------------------------
# Review, Wishlist, Profile
# -----------------------------
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(Profile)

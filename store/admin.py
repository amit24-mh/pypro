from django.contrib import admin
from .models import Category, Product, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')
    list_filter = ('user',)
    search_fields = ('product__name', 'user__username')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'full_name', 'phone')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('product',)
    search_fields = ('product__name', 'order__user__username')

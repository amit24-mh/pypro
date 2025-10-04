from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='home'),   # 👈 homepage
    path('cart/', views.view_cart, name='view_cart'),
    path('orders/', views.order_list, name='order_list'),
    path('checkout/', views.checkout, name='checkout'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
]

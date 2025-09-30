from django.urls import path
from store import views


urlpatterns = [
path('', views.product_list, name='product_list'),
path('product/<slug:slug>/', views.product_detail, name='product_detail'),
path('cart/', views.view_cart, name='view_cart'),
path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
path('checkout/', views.checkout, name='checkout'),
path('orders/', views.order_list, name='order_list'),
]
from django.urls import path
from . import views   # relative import of views from the same folder

urlpatterns = [
    path('', views.home, name='home'),  # example view
]


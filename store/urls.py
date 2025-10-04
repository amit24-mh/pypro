from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.home, login_url='login'), name='home'),
    path('cart/', login_required(views.view_cart), name='view_cart'),
    path('orders/', login_required(views.order_list), name='order_list'),
    path('checkout/', login_required(views.checkout), name='checkout'),
    path('product/<slug:slug>/', login_required(views.product_detail), name='product_detail'),
    path('cart/add/<int:product_id>/', login_required(views.add_to_cart), name='add_to_cart'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('create-superuser/', views.create_superuser_view, name='create_superuser'),
    path('redirect/', views.redirect_user, name='redirect_user'),

]

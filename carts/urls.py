from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('addProductToCart/<int:product_id>/', views.addProductToCart, name='addProductToCart'),
    path('removeProductFromCart/<int:product_id>/', views.removeProductFromCart, name='removeProductFromCart'),
    path('removeCartItem/<int:product_id>', views.removeCartItem, name='removeCartItem')
]
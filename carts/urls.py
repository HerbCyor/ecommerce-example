from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('addProductToCart/<int:product_id>/', views.addProductToCart, name='addProductToCart'),
    path('decreaseItemQuantity/<int:cart_item_id>/', views.decreaseItemQuantity, name='decreaseItemQuantity'),
    path('removeItemFromCart/<int:cart_item_id>', views.removeItemFromCart, name='removeItemFromCart'),
    path('increaseItemQuantity/<int:cart_item_id>', views.increaseItemQuantity, name='increaseItemQuantity'),
    path('checkout', views.checkout, name='checkout'),
    path('addShippingAddress', views.addShippingAddress, name='addShippingAddress'),
    path('selectShippingAddress/<int:address_id>', views.selectShippingAddress, name='selectShippingAddress'),
    path('updateShippingAddress/<int:address_id>', views.updateShippingAddress, name='updateShippingAddress'),
    path('removeShippingAddress/<int:address_id>', views.removeShippingAddress, name='removeShippingAddress'),
]
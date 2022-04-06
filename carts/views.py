from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product
from .models import Cart, CartItem
from django.http import HttpResponse
# Create your views here.

def _getCartIdbySession(request):
    ''' method for fetching session Id from cookies'''
    cartId = request.session.session_key

    if not cartId:
        cartId = request.session.create()

    return cartId

def addProductToCart(request, product_id):
    ''' adds a product to an existing unique Cart (CartId = sessionId), otherwise creates a new unique Cart first'''
    product = Product.objects.get(id=product_id)

    try:
        cart = Cart.objects.get(cart_id=_getCartIdbySession(request)) #get the cart using the cart_id present in the session

    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _getCartIdbySession(request)
        )
        cart.save()
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()

    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            cart = cart,
            quantity = 1
        )
        cart_item.save()

    return redirect('cart')

def removeProductFromCart(request, product_id):
    
    ''' gotta change this still '''
    
    cart = Cart.objects.get(cart_id=_getCartIdbySession(request))
    product = get_object_or_404(Product, id=product_id)
    item = CartItem.objects.get(product=product, cart=cart)
    if item.quantity > 0:
        item.quantity -=1
        item.save()
    
    if item.quantity == 0:
        item.delete()
    
    return redirect('cart')

def removeCartItem(request, product_id):
    cart = Cart.objects.get(cart_id=_getCartIdbySession(request))
    product = get_object_or_404(Product, id=product_id)
    item = CartItem.objects.get(product=product, cart=cart)
    item.delete()

    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):

    try:
        cart = Cart.objects.get(cart_id=_getCartIdbySession(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except Cart.DoesNotExist:
        pass

    context = {
        'total': total,
        'quantity':quantity,
        'cart_items': cart_items,
    }

    return render(request, 'store/cart.html', context)
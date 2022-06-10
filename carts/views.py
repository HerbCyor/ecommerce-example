from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from store.models import Product
from .models import Cart, CartItem
from accounts.models import ShippingAddress
from accounts.forms import ShippingAddressForm
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site

# Create your views here.

def _getCartIdbySession(request):
    ''' method for fetching session Id from cookies'''
    cartId = request.session.session_key

    if not cartId:
        cartId = request.session.create()

    return cartId

def getCurrentCart(request):
    ''' return Cart based on authentication'''
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).latest('date_added')
    else:
        cart = Cart.objects.get(cart_id=_getCartIdbySession(request))
    return cart

def addProductToCart(request, product_id):
    ''' adds a product to an existing unique Cart (CartId = sessionId), otherwise creates a new unique Cart first'''
    product = Product.objects.get(id=product_id)

    if request.method == 'POST':
        color = request.POST['color']
        size = request.POST['size']

    try:
        cart = getCurrentCart(request)
    except Cart.DoesNotExist:

        cart = Cart.objects.create(
            cart_id = _getCartIdbySession(request)
        )

        if request.user.is_authenticated:
            cart.user = request.user
        
        cart.save()
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, color=color, size=size)
        cart_item.quantity += 1
        cart_item.save()

    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            cart = cart,
            quantity = 1,
            color=color,
            size = size,
        )
        cart_item.save()

    return redirect('cart')

def decreaseItemQuantity(request, cart_item_id):
    
    ''' gotta change this still '''
    
    cart = getCurrentCart(request)
    item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
    # item = CartItem.objects.get(product=product, cart=cart)
    if item.quantity > 0:
        item.quantity -=1
        item.save()
    
    if item.quantity == 0:
        item.delete()
    
    return redirect('cart')

def increaseItemQuantity(request, cart_item_id):

    cart = getCurrentCart(request)    
    item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
    item.quantity +=1
    item.save()

    return redirect('cart')

def removeItemFromCart(request, cart_item_id):
    cart = getCurrentCart(request)
    item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
    # item = CartItem.objects.get(product=product, cart=cart)
    item.delete()

    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):

    try:
        cart = getCurrentCart(request)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass

    context = {
        'total': total,
        'quantity':quantity,
        'cart_items': cart_items,
    }

    return render(request, 'store/cart.html', context)

def addShippingAddress(request):

    url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            user = request.user
            data = form.cleaned_data
            try:
                for address in ShippingAddress.objects.filter(user=user):
                    address.is_selected = False
                    address.save()
            except:
                pass

            new_shipping_address = ShippingAddress.objects.create(user=user,**data)
            new_shipping_address.is_active = True
            new_shipping_address.is_selected = True
            new_shipping_address.save()
            messages.success(request, "yaay")
            return redirect(url)
        else:
            messages.error(request, "something here!!!")

def updateShippingAddress(request,address_id):
    #NOT IMPLEMENTED
    # url = request.META.get('HTTP_REFERER')
    user = request.user
    shipping_address = ShippingAddress.objects.get(user=user, pk=address_id)
    shipping_address_form = ShippingAddressForm(request.POST, instance=shipping_address)

    context = {
        'shipping_address_form':shipping_address_form,
        'shipping_address': shipping_address,
    }
    
    return render(request, 'store/checkout.html', context)

def selectShippingAddress(request, address_id):
    url = request.META.get('HTTP_REFERER')
    user = request.user
    selected_address = ShippingAddress.objects.get(user=user, pk=address_id)

    for address in ShippingAddress.objects.filter(user=user, is_active=True):
        if address.id == selected_address.id:
            address.is_selected = True
        else:
            address.is_selected = False
        address.save()
    return redirect(url)

def removeShippingAddress(request, address_id):
    url = request.META.get('HTTP_REFERER')
    user = request.user
    selected_address = ShippingAddress.objects.get(user=user, pk=address_id)
    selected_address.delete()
    return redirect(url)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    
    try:
        cart = getCurrentCart(request)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass

    user = request.user
    user_shipping_address = [_ for _ in ShippingAddress.objects.filter(user=user, is_active=True)]
    
    try:
        shipping_address = ShippingAddress.objects.get(user=user,is_active=True,is_selected=True)
    except(ShippingAddress.DoesNotExist):
        shipping_address = None

    shipping_address_form = ShippingAddressForm(request.POST)
    if shipping_address:
        order = str(cart.id) + '-' + str(shipping_address.id)
    else:
        order = "0"
    context = {
        'total': total,
        'quantity':quantity,
        'cart_items': cart_items,
        'user':user,
        'shipping_address':shipping_address,
        'shipping_address_form':shipping_address_form,
        'user_shipping_address':user_shipping_address,
        'order': order,
    }

    return render(request, 'store/checkout.html', context)
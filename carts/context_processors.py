from .models import Cart,CartItem
from .views import _getCartIdbySession

def cart_item_count(request):
    if 'admin' in request.path:
        return {}

    else:
        try:
            cart = Cart.objects.filter(cart_id=_getCartIdbySession(request))
            cart_items = CartItem.objects.all().filter(cart=cart[0])
            count = 0
            for item in cart_items:
                count += item.quantity
        except Cart.DoesNotExist:
            count = 0

    return {'cart_item_count':count}
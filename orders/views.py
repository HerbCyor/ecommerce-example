from django.http import JsonResponse
from django.shortcuts import render, redirect
from carts.models import Cart, CartItem
from accounts.models import ShippingAddress
from .models import Order, OrderItem, Payment
from django.contrib.auth.decorators import login_required
import json
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from carts.views import getCurrentCart
from django.core.mail import EmailMessage
# Create your views here.

def payment(request):
    
    user = request.user
    body = json.loads(request.body)
    order = Order.objects.get(user=user, is_ordered=False, order_number=body['orderID'] )
    
    #store transcations data inside payment model

    payment = Payment(
        user = user,
        payment_id=body['transID'],
        payment_method = body['payment_method'],
        amount = order.order_total,
        status = body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    for item in OrderItem.objects.all().filter(order=order):
        item.ordered = True
        item.save()

        #reduce stock

    #clear cart
    cart = getCurrentCart(request)
    CartItem.objects.filter(cart=cart).delete()
    
    #successful purchase email
    email = user.email
    current_site = get_current_site(request)
    mail_subject = "Thank you for your purchase. Your order has been completed."
    message = render_to_string("orders/order_received_email.html", {
        'user':user,
        'domain':current_site,
        'order': order,
    })
    send_email = EmailMessage(subject=mail_subject,body=message,to=[email])
    send_email.send()
    
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }

    return JsonResponse(data)

@login_required(login_url='login')
def place_order(request, order):

    cart_id,shipping_address_id = order.split('-')
    order_user = request.user
    order_cart = Cart.objects.get(id=cart_id)
    order_shipping_address = ShippingAddress.objects.get(id=shipping_address_id)
    new_order = Order(
        user = order_user,
        shipping_address=order_shipping_address,
        order_total=0,  
    )
    new_order.save()
    new_order.generate_order_number()
    
    cart_items = CartItem.objects.all().filter(cart=order_cart)
    total = 0

    for item in cart_items:
        total += item.product.price*item.quantity

        order_item = OrderItem(
            order = new_order,
            product = item.product,
            quantity = item.quantity,
            color = item.color,
            size = item.size,
            condition = item.condition,
        )
        order_item.save()
        
    new_order.order_total = total
    new_order.save()
    
    order_items = OrderItem.objects.all().filter(order=new_order)
    context = {
        'order':new_order,
        'order_items': order_items,
    }
    return render(request, 'orders/payment.html', context)

def order_complete(request):

    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number = order_number, is_ordered=True)
        order_items = OrderItem.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)
        shipping_address = order.shipping_address
        context = {
            'order':order,
            'order_items': order_items,
            'payment': payment,
            'shipping_address': shipping_address,
        }
    
        return render(request, 'orders/order_complete.html', context)

    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
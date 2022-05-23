from django.db import models
from accounts.models import Account, ShippingAddress
from store.models import Product

import datetime
# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=10)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=100)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)
    observations = models.TextField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)
    ip = models.CharField(max_length=100)
    order_total = models.FloatField(null=True)
    is_ordered = models.BooleanField(default=False)


    def __str__(self):
        return str(self.order_number)

    def generate_order_number(self):
        y = datetime.date.today().strftime("%Y")
        m = datetime.date.today().strftime("%m")
        d = datetime.date.today().strftime("%d")
        self.order_number = y+m+d + str(self.id)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    # Todo: add property to get color, size and more from store and create unique CartItem so if i choose the same product with diferent properties it creates a new CartItem
    color = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)
    condition = models.CharField(max_length=100, blank=True)
    ordered = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'OrderItem'
        verbose_name_plural = 'OrderItems'
    
    def __str__(self):
        return f"{self.product.product_name},{self.size},{self.color},{self.quantity}\n"

    def subtotal(self):
        return self.product.price*self.quantity
    
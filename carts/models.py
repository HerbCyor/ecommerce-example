from django.db import models
from store.models import Product
# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

    @property
    def cart_items(self):
        items = "".join([i.__str__() for i in CartItem.objects.filter(cart__cart_id=self.cart_id)])
        return items

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    # Todo: add property to get color, size and more from store and create unique CartItem so if i choose the same product with diferent properties it creates a new CartItem
    color = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)
    condition = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.product.product_name},{self.size},{self.color},{self.quantity}\n"

    def subtotal(self):
        return self.product.price*self.quantity
from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.

class CartAdmin(admin.ModelAdmin):
    readonly_fields = ('cart_items','date_added')
    fieldsets = (
        (None,{
            'fields': ('user','cart_id', 'cart_items', 'date_added')
            }),
            )

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
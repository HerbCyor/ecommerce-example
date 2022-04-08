from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.

class CartAdmin(admin.ModelAdmin):
    readonly_fields = ('cart_items',)
    fieldsets = (
        (None,{
            'fields': ('cart_id', 'cart_items')
            }),
            )

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
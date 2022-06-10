from django.contrib import admin
from .models import Payment, OrderItem, Order
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'order_total', 'status', ]
    
    readonly_fields = ('order_number','created_at', 'payment', 'order_total', 'ip')
    fieldsets = (
        (None,{
            'fields': (
                'order_number',
                'payment',
                'status',
                'shipping_address',
                'order_total',
                'created_at',
                'ip',
                'is_ordered',
                )
            }),
            )
# class OrderItemsAdmin(admin.ModelAdmin):
#     readonly_fields = ('cart',)
#     fieldsets = (
#         (None,{
#             'fields': ('content',)
#             }),
#             )
admin.site.register(Payment)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)

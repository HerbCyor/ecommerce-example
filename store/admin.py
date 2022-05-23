from django.contrib import admin
from .models import Product, ProductColor, ProductSize, ProductBrand, ProductCondition, ReviewRating

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug':('product_name',)}

class ProductBrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('brand',)}

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductColor)
admin.site.register(ProductSize)
admin.site.register(ProductBrand, ProductBrandAdmin)
admin.site.register(ProductCondition)
admin.site.register(ReviewRating)
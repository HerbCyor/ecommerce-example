from django.db import models
from category.models import Category
from django.urls import reverse
# Create your models here.

class ProductBrand(models.Model):
    brand = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.brand

class ProductSize(models.Model):
    size = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.size

class ProductColor(models.Model):
    color = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.color

class ProductCondition(models.Model):
    condition = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.condition

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    product_description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    
    brand = models.ForeignKey(ProductBrand, on_delete=models.CASCADE, null=True)
    size = models.ManyToManyField(ProductSize)
    color = models.ManyToManyField(ProductColor)
    condition = models.ManyToManyField(ProductCondition)

    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    def get_url(self):
        return reverse(
            'product_detail',
             kwargs={
                'category_slug': self.category.slug,
                'product_slug':self.slug}
                )
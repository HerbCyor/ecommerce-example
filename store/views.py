from tkinter import E
from django.shortcuts import get_object_or_404, render, redirect
from .models import Product, ReviewRating
from category.models import Category
from carts.models import CartItem
from carts.views import _getCartIdbySession
from django.core.paginator import EmptyPage, PageNotAnInteger,Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderItem
# Create your views here.
def store(request, category_slug=None):

    categories = None
    products = None

    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        product_count = products.count()
    
    
    #pagination
    paginator = Paginator(products,per_page=3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'product_count':product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):

    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_getCartIdbySession(request), product=single_product).exists()
    
    except Exception as e:
        raise e

    #TO DO : CHECK IF USER HAS BOUGHT THE PRODUCT BEFORE BEING ABLE TO POST A REVIEW 

    #GET REVIWES
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product':single_product,
        'in_cart': in_cart,
        'reviews':reviews,
    }

    return render(request, 'store/product_detail.html', context)

def search(request):

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']

        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(product_description__icontains=keyword) |  Q(product_name__icontains=keyword)) #pipe or backslash?
            product_count = products.count()

    context = {
        'products':products,
        'product_count':product_count,
    }
    return render(request,'store/store.html', context)

def submit_review(request, product_id):

    url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        
        try:
            review = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request, "Review Updated")
            return redirect(url)
        
        except(ReviewRating.DoesNotExist):
            
            form = ReviewForm(request.POST)
            
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.user = request.user
                data.product = Product.objects.get(id=product_id)
                data.save()
                messages.success(request, "Review Submitted")
                return redirect(url)

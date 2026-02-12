from django.shortcuts import render
from .models import Product
from category.models import Category
from django.shortcuts import get_object_or_404

from django.http import HttpResponse
from carts.views import _cart_id
from carts.models import CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator    
from django.db.models import Q

# Create your views here.

def store(request, category_slug = None):
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()
        paginator = Paginator(products, 2)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        products = paged_products
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 4)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
        products = paged_products
        
    context = {
        'products': products,
    }
    return render(request, 'store/store.html', context)

def product_detail (request, category_slug, product_slug):
    try:
        single_product = Product.objects.get( category__slug=category_slug, slug=product_slug )
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render (request, 'store/product_detail.html', context)

def search(request):
    products = None 
    context = {}

    if 'search' in request.GET:
        query = request.GET['search']
        
        if query:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=query) | Q(product_name__icontains=query)
            )
    context = {
        'products': products,
    }
    return render(request, 'store/store.html', context)
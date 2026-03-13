from django.shortcuts import redirect, render
from .models import Product, ReviewRating
from category.models import Category
from django.shortcuts import get_object_or_404

from django.http import HttpResponse
from carts.views import _cart_id
from carts.models import CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator    
from django.db.models import Q
from django.contrib.auth.decorators import login_required

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
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
        products = paged_products
        
    context = {
        'products': products,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'reviews': reviews, 
    }
    return render(request, 'store/product_detail.html', context)


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



login_required(login_url='login')
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            review = reviews
            review.subject = request.POST['subject']
            review.review = request.POST['review']
            review.rating = request.POST['rating']
            review.save()
            return redirect(url)
        except ReviewRating.DoesNotExist:
            review = ReviewRating.objects.create(
                user_id=request.user.id,
                product_id=product_id,
                subject=request.POST['subject'],
                review=request.POST['review'],
                rating=request.POST['rating'],
            )
            review.save()
            return redirect(url)
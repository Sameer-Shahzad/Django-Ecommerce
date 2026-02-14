from django.shortcuts import redirect, render

# Create your views here.
from .models import Payment, Order, OrderProduct
from carts.models import CartItem

from django.http import HttpResponse

def place_order(request, quantity=0, total=0):
    current_user = request.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total = (cart_item.product.price * cart_item.quantity)
        grand_total += total
        tax += (total * 0.02)
    
    if request.method == 'POST':
        data = Order()
        data.user = current_user
        data.first_name = request.POST['first_name']
        data.last_name = request.POST['last_name']
        data.phone = request.POST['phone']
        data.email = request.POST['email']
        data.address_line_1 = request.POST['address_line_1']
        data.address_line_2 = request.POST['address_line_2']
        data.country = request.POST['country']
        data.state = request.POST['state']
        data.city = request.POST['city']
        data.order_note = request.POST['order_note']
        data.order_total = 0
        data.tax = 0
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()
    

def payments(request):
    return HttpResponse("Payments Page Working!")

def order_complete(request):
    return HttpResponse("Order Complete Page Working!")
import os

from django.shortcuts import redirect, render
from django.conf import settings
# Create your views here.
from .models import Payment, Order, OrderProduct
from carts.models import CartItem

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import datetime
from decimal import Decimal


def payments(request):
    order_number = request.session.get('order_number')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=False)
        cart_items = CartItem.objects.filter(user=request.user)
        
        checkout_url = "https://sandbox.api.getsafepay.com/components"
        public_key = os.getenv("SAFEPAY_PUBLIC_KEY")
        
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': order.order_total - order.tax,
            'tax': order.tax,
            'grand_total': order.order_total,
            'safepay_public_key': settings.SAFEPAY_PUBLIC_KEY,
            'order_id': order.order_number,
        }
        
        return render(request, 'orders/payments.html', context)
        
    except Order.DoesNotExist:
        return redirect('checkout')
    

def payment_success(request):
    order_number = request.GET.get('order_id')
    payment_id = request.GET.get('tracker') 

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=False)
        
        payment = Payment(
            user = request.user,
            payment_id = payment_id,
            payment_method = 'Safepay',
            amount_paid = order.order_total,
            status = 'Completed',
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()


        CartItem.objects.filter(user=request.user).delete()

        context = {
            'order': order,
            'payment_id': payment_id,
        }
        return render(request, 'orders/order_complete.html', context)

    except Order.DoesNotExist:
        return redirect('home')
    
    
@login_required(login_url='login')
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
        # tax += (total * 0.02)
        tax += (total * Decimal("0.02"))
    
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
        data.order_total = grand_total
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()
        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        public_key = os.getenv("SAFEPAY_PUBLIC_KEY")
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'grand_total': float(order.order_total),
            'safepay_public_key': public_key,  
            'order_id': order_number,
        }
        request.session['order_number'] = order_number
        return render(request, 'orders/payments.html', context)
    
    else:
        return redirect('checkout')
    

def order_complete(request):
    return HttpResponse("Order Complete Page Working!")
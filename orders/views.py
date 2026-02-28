import os
import datetime
from decimal import Decimal
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Payment, Order, OrderProduct
from carts.models import CartItem

@login_required(login_url='login')
def place_order(request):
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

        request.session['order_number'] = order_number
        
        return redirect('payments')
    
    else:
        return redirect('checkout')

def payments(request):
    order_number = request.session.get('order_number')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=False)
        cart_items = CartItem.objects.filter(user=request.user)
        
        for item in cart_items:
            if not OrderProduct.objects.filter(order=order, product=item.product).exists():
                order_product = OrderProduct()
                order_product.order = order
                order_product.user = request.user
                order_product.product = item.product
                order_product.quantity = item.quantity
                order_product.product_price = item.product.price
                order_product.ordered = False 
                order_product.save()

                product_variation = item.variation.all()
                order_product.variation.set(product_variation)
                order_product.save()

        public_key = os.getenv("SAFEPAY_PUBLIC_KEY")
        
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': order.order_total - order.tax,
            'tax': order.tax,
            'grand_total': order.order_total,
            'safepay_public_key': public_key,
            'order_id': order_number,
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
        order.status = 'Accepted'
        order.save()

        order_products = OrderProduct.objects.filter(order=order)
        for item in order_products:
            item.ordered = True
            item.save()

        CartItem.objects.filter(user=request.user).delete()

        context = {
            'order': order,
            'payment_id': payment_id,
        }
        return render(request, 'orders/order_complete.html', context)

    except Order.DoesNotExist:
        return redirect('home')
    

def order_complete(request):
    pass
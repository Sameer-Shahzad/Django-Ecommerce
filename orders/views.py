import email
from email.message import EmailMessage
import os
import datetime
from decimal import Decimal
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Payment, Order, OrderProduct
from carts.models import CartItem
from accounts.models import Account
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator  
from store.models import Product, Variation
import hashlib
import hmac
import stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url='login')
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        cart_item.sub_total = cart_item.product.price * cart_item.quantity 
    
    tax = (total * Decimal("0.02"))
    grand_total = total + tax
    
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

        for item in cart_items:
            order_product = OrderProduct()
            order_product.order_id = data.id
            order_product.user_id = request.user.id
            order_product.product_id = item.product_id
            order_product.quantity = item.quantity
            order_product.product_price = item.product.price
            order_product.ordered = False
            order_product.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            order_product = OrderProduct.objects.get(id=order_product.id)
            order_product.variations.set(product_variation)
            order_product.save()

        request.session['order_number'] = order_number
    
        context = {
            'order': data,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'grand_total': grand_total,
        }
        
        return render(request, 'orders/payments.html', context)
    
    else:
        return redirect('checkout')
    
    
    
def payments(request):
    order_number = request.session.get('order_number')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=False)
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'pkr', 
                    'product_data': {'name': f'Order #{order.order_number}'},
                    'unit_amount': int(order.order_total * 100), 
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/orders/payment-success/') + f'?order_id={order.order_number}&session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=request.build_absolute_uri('/orders/payments/'),
        )
        
        return redirect(checkout_session.url, code=303)

    except Order.DoesNotExist:
        return redirect('home')



def payment_success(request):
    order_number = request.GET.get('order_id')
    payment_id = request.GET.get('session_id') 

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=False)
        
        payment = Payment(
            user = request.user,
            payment_id = payment_id,
            payment_method = 'Stripe',
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
            item.payment = payment
            item.ordered = True
            item.save()
            
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        CartItem.objects.filter(user=request.user).delete()

        mail_subject = 'Order Confirmed!'
        message = render_to_string('orders/order_complete_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        context = {
            'order': order,
            'payment_id': payment_id,
            'order_products': order_products,
        }
        return redirect(f'/orders/order-complete/?order_id={order_number}&session_id={payment_id}')

    except (Order.DoesNotExist, Exception) as e:
        print(f"Error: {e}")
        return redirect('home')




def order_complete(request):
    order_number = request.GET.get('order_id')
    payment_id = request.GET.get('session_id')

    try:

        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order=order)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'payment_id': payment_id,
        }
        return render(request, 'orders/order_complete.html', context)
    except Order.DoesNotExist:
        return redirect('home')
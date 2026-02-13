from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def place_order(request):
    # Abhi ke liye sirf message dikhane ke liye
    return HttpResponse("Place Order Page Working!")

def payments(request):
    return HttpResponse("Payments Page Working!")

def order_complete(request):
    return HttpResponse("Order Complete Page Working!")
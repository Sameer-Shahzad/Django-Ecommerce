from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('order-complete/', views.order_complete, name='order_complete'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('support/', views.support, name='support'),
    path('terms_of_service/', views.terms_of_service, name='terms_of_service'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
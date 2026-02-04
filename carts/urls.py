from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_all_cart/<int:product_id>/<int:cart_item_id>/', views.removeAll_cart, name='remove_all_cart'),
    path('checkout/', views.checkout, name='checkout'),  
    path('place_order/', views.place_order, name='place_order'),
]
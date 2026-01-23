from django.db import models

# Create your models here.
from accounts.models import Account
from store.models import Product, Variation

class Cart(models.Model):
    cart_id = models.CharField( max_length=250, blank=True )
    date_added = models.DateField(auto_now_add = True)
    
    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    variations = models.ManyToManyField(Variation, blank=True)
    # Is line mein null=True lazmi hai
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True) 
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.product)
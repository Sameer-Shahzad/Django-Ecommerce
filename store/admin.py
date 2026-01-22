from django.contrib import admin

# Register your models here.
from .models import Product, Variation

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('product_name',)}
    list_display = ('product_name', 'price','stock', 'modified_date', 'is_available', 'slug')

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active', 'created_date')
    list_editable = ('is_active',)
    
admin.site.register(Product, ProductAdmin) 
admin.site.register(Variation, VariationAdmin)
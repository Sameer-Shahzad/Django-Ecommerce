from django.contrib import admin

# Register your models here.


from .models import Payment, Order, OrderProduct

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'variation', 'color', 'size', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'first_name', 'last_name', 'phone', 'email', 'status', 'created_at', 'is_ordered')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'first_name', 'last_name', 'email')
    ordering = ('-created_at',)
    list_per_page = 20
    inlines = [OrderProductInline]      

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
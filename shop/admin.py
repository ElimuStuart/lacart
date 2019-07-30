from django.contrib import admin
from .models import Item, Order, OrderItem, Coupon, Refund

# Register your models here.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted', 'billing_address', 'coupon'
    ]
    search_fields = ['user__username', 'ref_code']
    list_display_links = ['user', 'coupon', 'billing_address']
    list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted']

admin.site.register(OrderItem)
admin.site.register(Coupon)
admin.site.register(Refund)


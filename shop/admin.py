from django.contrib import admin
from .models import Item, Order, OrderItem, Coupon, Refund, Address

def accept_refund(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)

accept_refund.short_description = "Accept Refund Request"

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted', 'billing_address', 'shipping_address', 'coupon'
    ]
    search_fields = ['user__username', 'ref_code']
    list_display_links = ['user', 'coupon', 'billing_address', 'shipping_address']
    list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted']
    actions=[accept_refund]


@admin.register(Address)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'street_address', 'apartment_address', 'country', 'zip', 'address_type', 'default'
    ]
    search_fields = ['user__username', 'street_address', 'apartment_address', 'zip']
    list_filter = ['default', 'address_type', 'country']

admin.site.register(OrderItem)
admin.site.register(Coupon)
admin.site.register(Refund)



from django.contrib import admin
from .models import Item, Order, OrderItem

# Register your models here.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered']

admin.site.register(OrderItem)
# admin.site.register(Order)


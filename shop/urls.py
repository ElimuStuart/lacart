from django.urls import path
from .views import item_list, product, checkout

app_name = 'shop'

urlpatterns = [
    path('', item_list, name="item_list"),
    path('product', product, name="product"),
    path('checkout', checkout, name="checkout"),
]

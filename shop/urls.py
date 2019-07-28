from django.urls import path
from .views import (
    index, product, checkout,
    add_to_cart,
    remove_from_cart,
)

app_name = 'shop'

urlpatterns = [
    path('', index, name="item_list"),
    path('category/<slug:tag_slug>/', index, name='item_list_by_category'),
    path('product/<slug>/', product, name="product"),
    path('product/<slug>/add-to-cart/', add_to_cart, name="add-to-cart"),
    path('product/<slug>/remove-from-cart/', remove_from_cart, name="remove-from-cart"),
    path('checkout', checkout, name="checkout"),
]

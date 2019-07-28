from django.urls import path
from .views import (
    index, product, checkout,
    add_to_cart,
    remove_from_cart,
    OrderSummaryView,
    remove_single_item_from_cart,
    add_single_item_to_cart,
)

app_name = 'shop'

urlpatterns = [
    path('', index, name="item_list"),
    path('category/<slug:tag_slug>/', index, name='item_list_by_category'),
    path('product/<slug>/', product, name="product"),
    path('product/<slug>/add-to-cart/', add_to_cart, name="add-to-cart"),
    path('product/<slug>/remove-from-cart/', remove_from_cart, name="remove-from-cart"),
    path('product/<slug>/remove_single_item_from_cart/', remove_single_item_from_cart, name="remove_single_item_from_cart"),
    path('product/<slug>/add_single_item_to_cart/', add_single_item_to_cart, name="add_single_item_to_cart"),
    path('product/<slug>/remove_single_item_from_cart/', remove_single_item_from_cart, name="remove_single_item_from_cart"),
    path('order_summary/', OrderSummaryView.as_view(), name="order_summary"),
    path('checkout', checkout, name="checkout"),
]

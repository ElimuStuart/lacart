from django.urls import path
from .views import index, product, checkout

app_name = 'shop'

urlpatterns = [
    path('', index, name="item_list"),
    path('category/<slug:tag_slug>/', index, name='item_list_by_category'),
    path('product/<slug>/', product, name="product"),
    path('checkout', checkout, name="checkout"),
]

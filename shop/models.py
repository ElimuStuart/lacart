from django.conf import settings
from taggit.managers import TaggableManager
from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField


# Create your models here.
LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    tags = TaggableManager() # categories
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField(max_length=250)
    description = models.TextField()


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:product', args=[
            self.slug
        ])

    def get_add_to_cart_url(self):
        return reverse('shop:add-to-cart', args=[
            self.slug
        ])

    def get_remove_from_cart_url(self):
        return reverse('shop:remove-from-cart', args=[
            self.slug
        ])

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    countries = CountryField(multiple=False)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
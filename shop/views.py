from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import DetailView, View
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from taggit.models import Tag
from .models import Item, OrderItem, Order
from .forms import CheckoutForm

# Create your views here.
def index(request, tag_slug=None):
    item_list = Item.objects.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        item_list = item_list.filter(tags__in=[tag])

    paginator = Paginator(item_list, 8)
    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = {
        'items': items,
        'tag': tag,
        'page': page
    }
    return render(request, "home-page.html", context)

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "Your cart is empty")
            return redirect("/")

@login_required
def product(request, slug):
    item = get_object_or_404(Item, slug=slug)
    item_tags_ids = item.tags.values_list('id', flat=True)
    similar_items = Item.objects.filter(tags__in=item_tags_ids).exclude(id=item.id)
    similar_items = similar_items.annotate(same_tags=Count('tags')).order_by('-same_tags')[:3]

    context = {
        'item': item,
        'similar_items': similar_items,
    }
    return render(request, "product-page.html", context)

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the orderitem is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item was updated to cart successfully")
            return redirect("shop:product", slug=slug)  
        else:
            order.items.add(order_item)
            messages.info(request, "Item was added to cart successfully")
            return redirect("shop:product", slug=slug)  

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item was added to cart successfully")
        return redirect("shop:product", slug=slug)  

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the orderitem is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                user=request.user,
                ordered=False
            )
            order.items.remove(order_item)
            messages.info(request, "Item was removed from your cart")
            return redirect("shop:order_summary")

    else:
    #    user doesnt have order
        return redirect("shop:product", slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the orderitem is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                user=request.user,
                ordered=False
            )
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else: 
                order.items.remove(order_item)
            messages.info(request, "Item quantity was updated")
            return redirect("shop:order_summary")

    else:
    #    user doesnt have order
        return redirect("shop:product", slug=slug)
    
@login_required
def add_single_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the orderitem is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item was updated to cart successfully")
            return redirect("shop:order_summary")  

class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {'form': form}
        return render(self.request, "checkout-page.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        if form.is_valid():
            return redirect("shop:checkout")
        
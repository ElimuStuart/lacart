from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q
from django.views.generic import DetailView, View
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect, reverse
from taggit.models import Tag
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm
from .models import Item, OrderItem, Order, Address, Coupon, Refund
from .forms import CheckoutForm, CouponForm, RefundForm

import random
import string

def generateRef(stringLength=6):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

def search(request):
    queryset = Item.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    paginator = Paginator(queryset, 12)
    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = {
        'items': items,
    }

    return render(request, 'search_results.html', context)

# Create your views here.
def index(request, tag_slug=None):
    item_list = Item.objects.all()
    cats = Tag.objects.all()
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
        'page': page,
        'cats': cats
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

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order
            }

            shipping_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]}
                )

            billing_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]}
                )

            return render(self.request, "checkout-page.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "Order does not exist")
            return redirect("shop:checkout")
        

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    print("using default shipping address")
                    shipping_address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type='S',
                        default=True
                    )
                    if shipping_address_qs.exists():
                        shipping_address = shipping_address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.error(self.request, "No default shipping address")
                        return redirect("shop:checkout")
                else:
                    print("user is entering shipping address")

                    shipping_address1 = form.cleaned_data.get('shipping_address')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    country = form.cleaned_data.get('shipping_country')
                    zip = form.cleaned_data.get('shipping_zip')
                    
                    if is_valid_form([shipping_address1, country, zip]):
                        shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_address1,
                            apartment_address = shipping_address2,
                            country = country,
                            zip = zip,
                            address_type='S'
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(self.request, "Please fill in all the required shipping address fields")

                
                use_default_billing = form.cleaned_data.get('use_default_billing')
                same_shipping_address = form.cleaned_data.get('same_shipping_address')

                if same_shipping_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                elif use_default_billing:
                    print("using default billing address")
                    billing_address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type='B',
                        default=True
                    )
                    if billing_address_qs.exists():
                        billing_address = billing_address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.error(self.request, "No default billing address")
                        return redirect("shop:checkout")
                else:
                    print("user is entering billing address")

                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    country = form.cleaned_data.get('billing_country')
                    zip = form.cleaned_data.get('billing_zip')
                    
                    if is_valid_form([billing_address1, country, zip]):
                        billing_address = Address(
                            user = self.request.user,
                            street_address = billing_address1,
                            apartment_address = billing_address2,
                            country = country,
                            zip = zip,
                            address_type='B'
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get('set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(self.request, "Please fill in all the required billing address fields")
                


                payment_option = form.cleaned_data.get('payment_option')
                order.ref_code = generateRef(20)
                
                self.request.session['ref_code'] = order.ref_code
                # return redirect('process_payment')
                if payment_option == 'P':
                    return redirect("shop:payment", payment_option='paypal')
                elif payment_option == 'M':
                    # return redirect("shop:payment", payment_option='momopay')
                    pass
                else:
                    messages.error(self.request, "Invalid option selected")
                    return redirect("shop:checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "Your cart is empty")
            return redirect("shop:order_summary")

        

def process_payment(request, payment_option):
    # order_id = request.session.get('order_id')
    # order = get_object_or_404(Order, id=order_id)
    order = Order.objects.get(user=request.user, ordered=False)
    host = request.get_host()
    if order.billing_address:
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': order.get_total(),
            'item_name': 'Order {}'.format(order.id),
            'invoice': order.ref_code,
            'currency_code': 'USD',
            'notify_url': 'http://{}{}'.format(host,
                                            reverse('paypal-ipn')),
            'return_url': 'http://{}{}'.format(host,
                                            reverse('shop:payment_done')),
            'cancel_return': 'http://{}{}'.format(host,
                                                reverse('shop:payment_cancelled')),
        }

        form = PayPalPaymentsForm(initial=paypal_dict)
        context = {
            'form': form,
            'order': order
        }
        return render(request, "payment.html", context)
    else:
        messages.error(request, "Please complete the checkout form")
        return redirect("shop:checkout")

@csrf_exempt
def payment_done(request):
    messages.info(request, "Your payment was successful")
    return redirect("shop:profile_summary")


@csrf_exempt
def payment_canceled(request):
    # return render(request, 'ecommerce_app/payment_cancelled.html')
    messages.error(request, "Your payment was not successful")
    return redirect("shop:order_summary")

@csrf_exempt
def profile_summary(request):
    my_orders = Order.objects.all().filter(user=request.user, ordered=True)
    # orders = my_orders[0]

    context = {
        'my_orders': my_orders
    }
    return render(request, 'profile.html', context)
    

def get_coupon(reqest, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.error(request, "This coupon does not exist")
        return redirect("shop:checkout")

class AddCouponView(View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            form = CouponForm(self.request.POST or None)
            if form.is_valid():
                try:
                    code = form.cleaned_data.get('code')
                    order = Order.objects.get(user=self.request.user, ordered=False)
                    order.coupon = get_coupon(self.request, code)
                    order.save()
                    messages.success(self.request, "Coupon added successfully")
                    return redirect("shop:checkout")
                except ObjectDoesNotExist:
                    messages.error(self.request, "Order does not exist")
                    return redirect("shop:checkout")


class RequestRefundView(View):
    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST or None)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')

            # edit order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested= True
                order.save()

                # save refund model
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                messages.success(self.request, "Your request was received. We will get back to you shortly.")
                return redirect("/")
            except ObjectDoesNotExist:
                    messages.error(self.request, "Order does not exist")
                    return redirect("shop:request-refund")
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request-refund.html", context)
        

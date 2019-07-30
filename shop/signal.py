from django.shortcuts import get_object_or_404
from .models import Order
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver


@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        # successful payment
        order = get_object_or_404(Order, id=ipn.item_name.split()[1])
        print(order.get_total())
        print(ipn.mc_gross)
        if order.get_total() == ipn.mc_gross:
            # mark the order as paid
            print(True)
            order.ordered = True
            print(order.save())
            order.save()
        print(False)
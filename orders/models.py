from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from userdata.models import Profile, AddressDeliveryProfile, ProfileBusiness, AddressPayment
from catalog.models import Product
from geodata.models import Country


class Order(models.Model):
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    PAYMENT_METHOD_NAME = (
        (1, 'PayPal'),
    )

    DELIVERY_TYPE = (
        (1, 'Standart'),
        (2, 'Express'),
    )

    seller = models.ForeignKey(ProfileBusiness)
    profile = models.ForeignKey(Profile)
    delivery_type = models.PositiveSmallIntegerField(choices=DELIVERY_TYPE, default=1)
    ship_to = models.ForeignKey(Country) #!!!
    number = models.CharField(max_length=50, blank=True)
    payment_method = models.PositiveSmallIntegerField(choices=PAYMENT_METHOD_NAME, default=1)
    note = models.TextField(blank=True, null=True)
    payment_status = models.BooleanField(default=False)
    payment_address = models.ForeignKey(AddressPayment, blank=True, null=True)
    shipping_address = models.ForeignKey(AddressDeliveryProfile, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)


class AmountProduct(models.Model):
    class Meta:
        verbose_name = 'String in order'
        verbose_name_plural = 'Strings in order'

    product = models.ForeignKey(Product)
    amount = models.IntegerField(default=0)
    delivery_price = models.IntegerField(blank=True, null=True)# XXX
    order = models.ForeignKey(Order)

    def __str__(self):
        return str(self.id)


class OrderStatus(models.Model):
    class Meta:
        verbose_name = 'Order status'
        verbose_name_plural = 'Order statuses'

    ORDER_STATUS = (
        (1, 'new'),
        (2, 'paid for'),
        (3, 'ready to ship'),
        (4, 'canceled'),
        (5, 'shipped'),
        (6, 'delivered'),
        (7, 'failed'),
    )

    order = models.ForeignKey(Order)
    status = models.PositiveSmallIntegerField(choices=ORDER_STATUS)
    comment = models.CharField(max_length=256, blank=True, null=True)
    customer_notificated = models.BooleanField(default=0)
    tracking_number = models.CharField(max_length=25, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.status)


@receiver(post_save, sender=Order)
def new_order_status(sender, instance=None, created=False, **kwargs):
    if created:
        OrderStatus.objects.create(order=instance, status=1)

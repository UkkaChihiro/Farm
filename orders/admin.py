from django.contrib import admin
from .models import Order, AmountProduct, OrderStatus


class AmountProductInline(admin.TabularInline):
    model = AmountProduct


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [AmountProductInline]
    readonly_fields = ('status',)
    list_display = ['id', 'seller', 'profile', 'delivery_type', 'status', 'weight']

    def status(self, obj):
        return OrderStatus.objects.filter(order=obj).order_by('-id').first().status

    def weight(self, obj):
        return sum(pr.product.weight_of_pack*pr.amount for pr in AmountProduct.objects.filter(order=obj))


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_id', 'status']

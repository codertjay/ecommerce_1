from django.contrib import admin
from.models import OrderItem,Item,Order


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)

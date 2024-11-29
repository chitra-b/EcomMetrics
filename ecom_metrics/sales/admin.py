from django.contrib import admin
from .models import Product, Customer, Address, Delivery, Order

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(Delivery)
admin.site.register(Order)

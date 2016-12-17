from django.contrib import admin

from .models import Customers, Products, Reservations

# Register your models here.
admin.site.register(Customers)
admin.site.register(Products)
admin.site.register(Reservations)

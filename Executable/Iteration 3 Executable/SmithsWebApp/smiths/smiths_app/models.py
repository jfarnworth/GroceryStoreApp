from django.db import models


class Customers(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    is_active = models.NullBooleanField()
    point_balance = models.IntegerField(blank=True, null=True)
    receipts = models.TextField(blank=True, null=True)
    reservations = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customers'

    def __str__(self):
        return self.name


class Products(models.Model):
    name = models.TextField()
    barcode = models.IntegerField(primary_key=True)
    available_units = models.TextField()
    customer_price = models.TextField(blank=True, null=True)
    price = models.TextField(blank=True, null=True)
    weigh_b = models.IntegerField(blank=True, null=True)
    provider = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'

    def __str__(self):
        return self.name


class Reservations(models.Model):
    id = models.IntegerField(primary_key=True)
    r_date = models.TextField(blank=True, null=True)
    quantities = models.TextField(blank=True, null=True)
    customer_id = models.IntegerField(blank=True, null=True)
    barcodes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reservations'

    def __str__(self):
        return self.r_date

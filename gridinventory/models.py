from django.db import models
from gridaccounts.models import *

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    product_image = models.ImageField(upload_to="products/", null=True, blank=True)
    product_name = models.CharField(max_length=255)
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    vendor_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Price per unit
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Price per unit

    quantity = models.PositiveIntegerField(null=True, blank=True)  # Stock available

    def __str__(self):
        return f"{self.product_name} - {self.product_category.name}"
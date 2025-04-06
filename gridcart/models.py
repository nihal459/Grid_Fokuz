from django.db import models
from gridinventory.models import *
from gridaccounts.models import *

# Create your models here.
class AddToCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE, null=True, blank=True)
    profit_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=True, default=0.00)
    branding_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=True, default=0.00)
    branding_category = models.CharField(max_length=255, null=True, blank=True)
    transportation_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=True, default=0.00)
    tax_precentage = models.DecimalField(max_digits=10, decimal_places=2, editable=True, default=0.00)
    date_added = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=True, default=0.00)

    def __str__(self):
        return f"{self.product.product_name} added on {self.date_added}"


    
class OrderedProduct(models.Model):
    checkout = models.ForeignKey(AddToCart, on_delete=models.CASCADE, related_name='ordered_products')
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.checkout.date_added}"


class Logo(models.Model):
    image = models.ImageField(upload_to="Logo1")

    def __str__(self):
        return str(self.image)
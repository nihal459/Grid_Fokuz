from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal
from django.db.models import Q
from gridinventory.models import *

# Create your views here.


# Fetch salesmen matching the query
def search_salesmen(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Ensure AJAX request
        query = request.GET.get('term', '').strip()
        salesmen = Vendor.objects.filter(name__icontains=query)[:10]
        salesman_list = [{"label": s.name, "value": s.name} for s in salesmen]
        return JsonResponse(salesman_list, safe=False)
    return JsonResponse([], safe=False)



def filter_products(request):
    products = Inventory.objects.all()

    # Get filters from request
    q = request.GET.get("q")
    vendors = request.GET.getlist("vendor")
    categories = request.GET.getlist("category")
    subcategories = request.GET.getlist("subcategory")
    min_vendor_price = request.GET.get("min_vendor_price")
    max_vendor_price = request.GET.get("max_vendor_price")
    min_mrp = request.GET.get("min_mrp")
    max_mrp = request.GET.get("max_mrp")

    # Apply Filters
    if q:
        products = products.filter(product_name__icontains=q)  # Fix for search
    if vendors:
        products = products.filter(vendor__id__in=vendors)
    if categories:
        products = products.filter(product_category__id__in=categories)  # Fix for category filtering
    if subcategories:
        products = products.filter(product_subcategory__id__in=subcategories) 
    if min_vendor_price:
        products = products.filter(vendor_price__gte=min_vendor_price)
    if max_vendor_price:
        products = products.filter(vendor_price__lte=max_vendor_price)
    if min_mrp:
        products = products.filter(mrp__gte=min_mrp)
    if max_mrp:
        products = products.filter(mrp__lte=max_mrp)

    return render(request, "partials/product_rows.html", {"products": products})



# def filter_pdf(request):
#     vendors = Vendor.objects.all()
#     categories = Category.objects.all()
#     subcategories = SubCategory.objects.all()
#     products = Inventory.objects.all()
#     return render(request, "filter_pdf.html", {"vendors": vendors, "categories": categories, "products": products, 'subcategories':subcategories})

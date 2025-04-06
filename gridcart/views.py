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
import random




        


# def add_to_cart2(request, product_id):
#     product = get_object_or_404(Inventory, id=product_id)

#     # Check if product is already in cart
#     cart_item, created = AddToCart.objects.get_or_create(product=product)

#     if not created:
#         # Product already exists, no need to add again
#         pass
    
#     return redirect('filter_pdf') 


from django.contrib.auth.decorators import login_required

# @login_required
# def add_product_to_pdf(request, product_id):
#     if request.method == "GET":
#         product = get_object_or_404(Inventory, pk=product_id)

#         # Ensure the user's ID is stored in the cart
#         cart_item, created = AddToCart.objects.get_or_create(
#             user=request.user, 
#             product=product,
#             defaults={
#                 "price": product.vendor_price,  # Adjust this field if needed
#             }
#         )

#         if created:
#             message = f"{product.product_name} added to PDF successfully!"
#         else:
#             message = f"{product.product_name} is already in your PDF cart."

#         return JsonResponse({"message": message})

#     return JsonResponse({"error": "Invalid request"}, status=400)



from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Vendor, Category, SubCategory, Inventory, AddToCart

@login_required
def filter_pdf(request):
    vendors = Vendor.objects.all()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    products = Inventory.objects.all()
    return render(request, "filter_pdf.html", {
        "vendors": vendors,
        "categories": categories,
        "subcategories": subcategories,
        "products": products
    })

@login_required
def filter_products(request):
    products = Inventory.objects.all()
    
    # Apply filters
    if q := request.GET.get('q'):
        products = products.filter(product_name__icontains=q)
    
    if vendor_ids := request.GET.getlist('vendor'):
        products = products.filter(vendor__id__in=vendor_ids)
    
    if category_ids := request.GET.getlist('category'):
        products = products.filter(product_category__id__in=category_ids)
    
    if subcategory_ids := request.GET.getlist('subcategory'):
        products = products.filter(product_subcategory__id__in=subcategory_ids)
    
    if min_price := request.GET.get('min_vendor_price'):
        products = products.filter(vendor_price__gte=min_price)
    
    if max_price := request.GET.get('max_vendor_price'):
        products = products.filter(vendor_price__lte=max_price)
    
    if min_mrp := request.GET.get('min_mrp'):
        products = products.filter(mrp__gte=min_mrp)
    
    if max_mrp := request.GET.get('max_mrp'):
        products = products.filter(mrp__lte=max_mrp)
    
    return render(request, "partials/product_rows.html", {"products": products})

@login_required
def add_product_to_pdf(request, product_id):
    if request.method == "GET":
        product = get_object_or_404(Inventory, pk=product_id)
        
        cart_item, created = AddToCart.objects.get_or_create(
            user=request.user, 
            product=product,
            defaults={"price": product.vendor_price}
        )
        
        message = (
            f"{product.product_name} added to PDF successfully!" if created
            else f"{product.product_name} is already in your PDF cart."
        )
        
        return JsonResponse({"message": message})
    
    return JsonResponse({"error": "Invalid request"}, status=400)




@login_required
def empty_whole_cart(request):
    if request.method == "GET" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        user = request.user
        AddToCart.objects.filter(user=user).delete()  # Delete only the user's cart items
        return JsonResponse({"message": "Your cart has been emptied successfully!", "status": "success"})

    return JsonResponse({"message": "Invalid request", "status": "error"}, status=400)


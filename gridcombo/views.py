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
from gridcart.models import *

def combo_pdf(request):
    if request.method == "POST":
        request.session['price_range'] = int(request.POST['price_range'])
        return redirect('combo_step2')
    return render(request, "combo_pdf.html")


def combo_step2(request):
    price_range = request.session.get('price_range')

    # Get vendors within the price range
    vendors = Vendor.objects.filter(inventory__vendor_price__lte=price_range).distinct()

    if request.method == "POST":
        selected_vendors = request.POST.getlist('vendors')
        
        if not selected_vendors:
            messages.error(request, "Please select at least one vendor.")
            return render(request, "combo_step2.html", {"vendors": vendors})

        request.session['selected_vendors'] = selected_vendors
        return redirect('combo_step3')

    return render(request, "combo_step2.html", {"vendors": vendors})



def combo_step3(request):
    price_range = request.session.get('price_range')
    selected_vendors = request.session.get('selected_vendors', [])
    categories = Category.objects.filter(
        inventory__vendor__id__in=selected_vendors,
        inventory__vendor_price__lte=price_range
    ).distinct()

    if request.method == "POST":
        selected_categories = request.POST.getlist('categories')

        if not selected_categories:
            messages.error(request, "Please select at least one category.")
            return render(request, "combo_step3.html", {"categories": categories})
        
        if selected_categories:
            request.session['selected_categories'] = selected_categories
            return redirect('combo_step4')
        


    return render(request, "combo_step3.html", {"categories": categories})


def combo_step4(request):
    if request.method == "POST":
        request.session['combo_count'] = int(request.POST['combo_count'])
        request.session['min_products'] = int(request.POST['min_products'])
        return redirect('generate_combos')
    return render(request, "combo_step4.html")


def generate_combos(request):
    price_range = request.session.get('price_range')
    selected_vendors = request.session.get('selected_vendors', [])
    selected_categories = request.session.get('selected_categories', [])
    combo_count = request.session.get('combo_count', 1)
    min_products = request.session.get('min_products', 1)

    all_products = list(Inventory.objects.filter(
        vendor__id__in=selected_vendors,
        product_category__id__in=selected_categories,
        vendor_price__lte=price_range
    ))

    # Error Handling: Check if there are enough products
    if not all_products:
        return render(request, "combo_result.html", {
            "error": "No products available to create a combo within the selected filters."
        })

    total_inventory_value = sum(product.vendor_price for product in all_products)
    max_product_price = max(product.vendor_price for product in all_products)

    # Error Handling: Check if the price range is too high
    if total_inventory_value < price_range:
        return render(request, "combo_result.html", {
            "error": "The entered price range is too high. Not enough products available."
        })

    # Error Handling: If even the most expensive product is above the price range
    if max_product_price > price_range:
        return render(request, "combo_result.html", {
            "error": "No single product fits within the selected price range."
        })

    combos = []

    for _ in range(combo_count):
        random.shuffle(all_products)  # Shuffle the list to ensure variety
        combo = []
        total_price = 0

        for product in all_products:
            if total_price + product.vendor_price <= price_range and product not in combo:
                combo.append(product)
                total_price += product.vendor_price

            if len(combo) >= min_products and total_price >= price_range * 0.9:
                break  # Stop if conditions are met

        # Error Handling: If the generated combo does not meet the minimum number of products
        if len(combo) < min_products:
            return render(request, "combo_result.html", {
                "error": "Not able to make a combo with the chosen price range and minimum product requirement."
            })

        combos.append(combo)

    return render(request, "combo_result.html", {"combos": combos})


# def add_to_cart3(request, product_id):
#     if request.method == "GET" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
#         product = get_object_or_404(Inventory, id=product_id)

#         # Check if the product is already in the cart
#         cart_item, created = AddToCart.objects.get_or_create(product=product)

#         if created:
#             message = "Product added to cart!"
#         else:
#             message = "Product is already in the cart!"

#         return JsonResponse({"message": message, "status": "success"})

#     return JsonResponse({"message": "Invalid request", "status": "error"}, status=400)



# @csrf_exempt  
# def add_whole_combo_to_cart(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)  # Parse JSON request data
#             product_ids = data.get("product_ids", [])

#             if not product_ids:
#                 return JsonResponse({"message": "No products received", "status": "error"}, status=400)

#             added_products = []
#             already_in_cart = []

#             for product_id in product_ids:
#                 product = get_object_or_404(Inventory, id=product_id)
#                 cart_item, created = AddToCart.objects.get_or_create(product=product)

#                 if created:
#                     added_products.append(product.product_name)
#                 else:
#                     already_in_cart.append(product.product_name)

#             return JsonResponse({
#                 "message": "Combo added to cart successfully!",
#                 "status": "success",
#                 "added_products": added_products,
#                 "already_in_cart": already_in_cart
#             })

#         except Exception as e:
#             return JsonResponse({"message": str(e), "status": "error"}, status=400)

#     return JsonResponse({"message": "Invalid request", "status": "error"}, status=400)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@require_http_methods(["GET"])
def add_to_cart3(request, product_id):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"message": "Bad request", "status": "error"}, status=400)
    
    product = get_object_or_404(Inventory, id=product_id)
    cart_item, created = AddToCart.objects.get_or_create(
        product=product,
        user=request.user if request.user.is_authenticated else None
    )
    
    return JsonResponse({
        "message": "Product added to cart!" if created else "Product already in cart!",
        "status": "success"
    })

@csrf_exempt
@require_http_methods(["POST"])
def add_whole_combo_to_cart(request):
    try:
        data = json.loads(request.body)
        product_ids = data.get("product_ids", [])
        
        if not product_ids:
            return JsonResponse({"message": "No products received", "status": "error"}, status=400)

        results = {
            "added": [],
            "existing": []
        }

        for product_id in product_ids:
            product = get_object_or_404(Inventory, id=product_id)
            _, created = AddToCart.objects.get_or_create(
                product=product,
                user=request.user if request.user.is_authenticated else None
            )
            results["added" if created else "existing"].append(product.product_name)

        return JsonResponse({
            "message": "Combo processed",
            "status": "success",
            "results": results
        })

    except Exception as e:
        return JsonResponse({"message": str(e), "status": "error"}, status=400)
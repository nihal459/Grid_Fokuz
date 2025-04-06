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
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os
from django.contrib.auth.decorators import login_required
from datetime import datetime



@login_required
def invoice(request):
    user = request.user
    cart_items = AddToCart.objects.filter(user=user)
    return render(request, "invoice.html", {"cart_items": cart_items})


def remove_product(request, product_id):
    product = get_object_or_404(OrderedProduct, id=product_id)
    invoice_id = product.checkout.id
    product.delete()
    return redirect("edit_invoice", invoice_id=invoice_id)



# def generate_cart_pdf(request):
#     if not request.user.is_authenticated:
#         return redirect('sales_login')

#     # Get user's cart items
#     cart_items = AddToCart.objects.filter(user=request.user)

#     if not cart_items.exists():
#         return HttpResponse("Cart is empty!", content_type="text/plain")

#     # Save cart items to OrderedProduct before clearing the cart
#     for item in cart_items:
#         OrderedProduct.objects.create(
#             checkout=item,  # Linking to the AddToCart instance
#             product=item.product
#         )


#     # Get logos
#     logo1 = Logo.objects.get(id=1)
#     logo2 = Logo.objects.get(id=2)
#     logo3 = Logo.objects.get(id=5)
#     logo4 = Logo.objects.get(id=3)
#     logo5 = Logo.objects.get(id=6)
#     logo6 = Logo.objects.get(id=4)

#     # Ensure product image paths are correct
#     for item in cart_items:
#         if item.product and item.product.product_image:
#             item.product.image_path = os.path.join(settings.MEDIA_ROOT, item.product.product_image.name)
#         else:
#             item.product.image_path = None  # Avoid errors if no image

#     # Context for the template
#     context = {
#         'cart_items': cart_items,
#         'logo1': logo1,
#         'logo2': logo2,
#         'logo3': logo3,
#         'logo4': logo4,
#         'logo5': logo5,
#         'logo6': logo6,
#     }

#     # Render template to HTML
#     template_path = 'make_pdf.html'
#     template = get_template(template_path)
#     html = template.render(context)

#     current_date = datetime.now().strftime('%Y-%m-%d')
#     filename = f"GridFokuz_{current_date}.pdf"

#     # Create PDF response
#     response = HttpResponse(content_type='application/pdf')
#     # response['Content-Disposition'] = 'attachment; filename="GridFokuz.pdf"'
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     # Generate PDF
#     pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
#     cart_items.delete()

#     if pisa_status.err:
#         return HttpResponse("Error generating PDF")

#     return response



def generate_cart_pdf(request):
    if not request.user.is_authenticated:
        return redirect('sales_login')

    cart_items = AddToCart.objects.filter(user=request.user)

    if not cart_items.exists():
        return HttpResponse("Cart is empty!", content_type="text/plain")

    # Save to OrderedProduct (optional depending on business logic)
    for item in cart_items:
        OrderedProduct.objects.create(
            checkout=item,
            product=item.product
        )

    # Load logos
    logo1 = Logo.objects.get(id=1)
    logo2 = Logo.objects.get(id=2)
    logo3 = Logo.objects.get(id=5)
    logo4 = Logo.objects.get(id=3)
    logo5 = Logo.objects.get(id=6)
    logo6 = Logo.objects.get(id=4)

    for item in cart_items:
        if item.product and item.product.product_image:
            item.product.image_path = os.path.join(settings.MEDIA_ROOT, item.product.product_image.name)
        else:
            item.product.image_path = None

    # Get checkbox options from query parameters
    include_branding_cost = request.GET.get('branding_cost') == '1'
    include_branding_category = request.GET.get('branding_category') == '1'
    include_transportation_cost = request.GET.get('transportation_cost') == '1'
    include_tax_percentage = request.GET.get('tax_percentage') == '1'
    include_price = request.GET.get('price') == '1'

    context = {
        'cart_items': cart_items,
        'logo1': logo1,
        'logo2': logo2,
        'logo3': logo3,
        'logo4': logo4,
        'logo5': logo5,
        'logo6': logo6,

        # Pass checkbox states to template
        'include_branding_cost': include_branding_cost,
        'include_branding_category': include_branding_category,
        'include_transportation_cost': include_transportation_cost,
        'include_tax_percentage': include_tax_percentage,
        'include_price': include_price,
    }

    template = get_template('make_pdf.html')
    html = template.render(context)

    current_date = datetime.now().strftime('%Y-%m-%d')
    filename = f"GridFokuz_{current_date}.pdf"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    cart_items.delete()

    if pisa_status.err:
        return HttpResponse("Error generating PDF")

    return response

# Ensure correct media file path resolution
def link_callback(uri, rel):
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
        return path
    return uri


def search_products(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Ensure AJAX request
        query = request.GET.get('term', '').strip()
        products = Inventory.objects.filter(product_name__icontains=query)[:10]
        product_list = [{"label": p.product_name, "value": p.product_name} for p in products]
        return JsonResponse(product_list, safe=False)
    return JsonResponse([], safe=False)



from django.contrib.auth.decorators import login_required

@login_required
def add_to_cart(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name", "").strip()

        # Check if input is empty
        if not product_name:
            messages.error(request, "Nothing to add")
            return redirect("invoice")

        try:
            product = Inventory.objects.get(product_name__iexact=product_name)  # Case-insensitive lookup

            # Check if product already in cart for this user
            cart_item, created = AddToCart.objects.get_or_create(product=product, user=request.user)

            if created:
                messages.success(request, f"{product_name} added to pdf cart")
            else:
                messages.info(request, f"{product_name} is already in your cart")

        except Inventory.DoesNotExist:
            messages.error(request, "Invalid product, not present in inventory")

    return redirect("invoice")




# @csrf_exempt
# def update_cart_item(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             item_id = data.get("item_id")
#             mrp = float(data.get("mrp", 0))
#             profit_amount = float(data.get("profit_amount", 0))
#             branding_cost = float(data.get("branding_cost", 0))
#             transportation_cost = float(data.get("transportation_cost", 0))
#             tax_percentage = float(data.get("tax_percentage", 0))
#             branding_category = data.get("branding_category", "")
#             total_price = float(data.get("total_price", 0))

#             # Update the corresponding cart item
#             cart_item = AddToCart.objects.get(id=item_id)
#             cart_item.product.mrp = mrp
#             cart_item.profit_amount = profit_amount
#             cart_item.branding_cost = branding_cost
#             cart_item.transportation_cost = transportation_cost
#             cart_item.tax_precentage = tax_percentage
#             cart_item.branding_category = branding_category
#             cart_item.price = total_price
#             cart_item.save()

#             return JsonResponse({"success": True, "updated_price": total_price})
#         except AddToCart.DoesNotExist:
#             return JsonResponse({"success": False, "error": "Cart item not found"})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})
#     return JsonResponse({"success": False, "error": "Invalid request"}, status=400)



@csrf_exempt
def update_cart_item(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            item_id = data.get("item_id")
            vendor_price = float(data.get("vendor_price", 0))
            mrp = float(data.get("mrp", 0))
            profit_amount = float(data.get("profit_amount", 0))
            branding_cost = float(data.get("branding_cost", 0))
            transportation_cost = float(data.get("transportation_cost", 0))
            tax_percentage = float(data.get("tax_percentage", 0))
            branding_category = data.get("branding_category", "")
            
            # Calculate total price (same logic as frontend)
            subtotal = vendor_price + profit_amount + branding_cost + transportation_cost
            tax_amount = (tax_percentage / 100) * subtotal
            total_price = subtotal + tax_amount

            # Update the cart item
            cart_item = AddToCart.objects.get(id=item_id)
            cart_item.product.vendor_price = vendor_price
            cart_item.product.mrp = mrp
            cart_item.profit_amount = profit_amount
            cart_item.branding_cost = branding_cost
            cart_item.transportation_cost = transportation_cost
            cart_item.tax_precentage = tax_percentage
            cart_item.branding_category = branding_category
            cart_item.price = total_price
            cart_item.save()

            return JsonResponse({
                "success": True,
                "updated_price": total_price
            })
        except AddToCart.DoesNotExist:
            return JsonResponse({"success": False, "error": "Cart item not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)



@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')

        try:
            cart_item = AddToCart.objects.get(id=item_id)
            cart_item.delete()
            return JsonResponse({'success': True})
        except AddToCart.DoesNotExist:
            return JsonResponse({'success': False})
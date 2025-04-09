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
import os 
# Create your views here.


def manage_category(request):
    query = request.GET.get('q', '').strip()  # Get search query and remove extra spaces
    
    if query:
        categories = Category.objects.filter(name__icontains=query)  # Filter categories based on query
    else:
        categories = Category.objects.all()

    if request.method == "POST":
        category_name = request.POST.get('category_name').strip()  # Remove extra spaces

        if category_name:
            # Check if category with the same name (case-insensitive) already exists
            if Category.objects.filter(name__iexact=category_name).exists():
                messages.error(request, "This category already exists!")  # Show error message
            else:
                Category.objects.create(name=category_name)  # Create new category
                messages.success(request, "Category added successfully!")  # Show success message
                return redirect('manage_category')

    return render(request, 'manage_category.html', {'categories': categories, 'query': query})




def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        new_name = request.POST.get('category_name')

        # Check if the new name is different and already exists
        if new_name != category.name and Category.objects.filter(name=new_name).exists():
            return JsonResponse({'error': 'This category already exists'}, status=400)

        try:
            category.name = new_name
            category.save()
            return JsonResponse({'success': 'Category updated successfully'})
        except IntegrityError:
            return JsonResponse({'error': 'This category already exists'}, status=400)

    return JsonResponse({'name': category.name})


def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('manage_category')



def manage_subcategory(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    # Search functionality
    query = request.GET.get('q', '').strip()  # Get search query from request
    if query:
        subcategories = subcategories.filter(
            category__name__icontains=query  # Search by category name
        ) | subcategories.filter(
            name__icontains=query  # Search by subcategory name
        )

    if request.method == "POST":
        category_id = request.POST.get('category')  # Get selected category ID
        subcategory_name = request.POST.get('subcategory_name').strip()  # Get subcategory name & remove extra spaces

        if category_id and subcategory_name:
            category = Category.objects.get(id=category_id)  # Fetch category instance

            # Check if the subcategory already exists in the same category
            if SubCategory.objects.filter(category=category, name__iexact=subcategory_name).exists():
                messages.error(request, "This subcategory already exists!")  # Show error alert
            else:
                SubCategory.objects.create(category=category, name=subcategory_name)  # Create subcategory
                messages.success(request, "Subcategory added successfully!")  # Show success alert
                return redirect('manage_subcategory')

    return render(request, 'manage_subcategory.html', {
        'categories': categories,
        'subcategories': subcategories,
        'query': query,  # Pass search query back to the template
    })


def edit_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    if request.method == 'POST':
        new_name = request.POST.get('subcategory_name', '').strip()

        if SubCategory.objects.exclude(id=subcategory_id).filter(name=new_name).exists():
            return JsonResponse({'error': 'Subcategory name must be unique.'})

        subcategory.name = new_name
        subcategory.save()
        messages.success(request, 'Subcategory updated successfully!')
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'})


def delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    subcategory.delete()
    messages.success(request, "Subcategory deleted successfully!")
    
    return redirect('manage_subcategory') 



def manage_products(request):
    query = request.GET.get("q", "")
    vendor_filter = request.GET.getlist("vendor")  # Multi-select
    category_filter = request.GET.getlist("category")  # Multi-select
    subcategory_filter = request.GET.getlist("subcategory")  # Multi-select
    min_vendor_price = request.GET.get("min_vendor_price", "")
    max_vendor_price = request.GET.get("max_vendor_price", "")
    min_mrp = request.GET.get("min_mrp", "")
    max_mrp = request.GET.get("max_mrp", "")

    materials = Inventory.objects.all()

    # **Basic Search** (by product name, category, subcategory, vendor)
    if query:
        materials = materials.filter(
            Q(product_name__icontains=query) |
            Q(product_category__name__icontains=query) |
            Q(product_subcategory__name__icontains=query) |
            Q(vendor__name__icontains=query)
        )

    # **Advanced Filtering**
    if vendor_filter:
        materials = materials.filter(vendor__id__in=vendor_filter)

    if category_filter:
        materials = materials.filter(product_category__id__in=category_filter)

    if subcategory_filter:
        materials = materials.filter(product_subcategory__id__in=subcategory_filter)

    if min_vendor_price:
        materials = materials.filter(vendor_price__gte=min_vendor_price)

    if max_vendor_price:
        materials = materials.filter(vendor_price__lte=max_vendor_price)

    if min_mrp:
        materials = materials.filter(mrp__gte=min_mrp)

    if max_mrp:
        materials = materials.filter(mrp__lte=max_mrp)

    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    subcategories = SubCategory.objects.all()

    return render(request, "manage_products.html", {
        "materials": materials,
        "categories": categories,
        "vendors": vendors,
        "subcategories": subcategories
    })






def add_material(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        category_id = request.POST.get("product_category")
        subcategory_id = request.POST.get("product_subcategory")
        vendor_id = request.POST.get("vendor")
        vendor_price = request.POST.get("vendor_price")
        mrp = request.POST.get("mrp")
        product_image = request.FILES.get("product_image")  # Handle file upload

        category = get_object_or_404(Category, id=category_id)
        subcategory = get_object_or_404(SubCategory, id=subcategory_id) if subcategory_id else None
        vendor = get_object_or_404(Vendor, id=vendor_id) if vendor_id else None

        Inventory.objects.create(
            product_name=product_name,
            product_category=category,
            product_subcategory=subcategory,
            vendor=vendor,
            vendor_price=vendor_price,
            mrp=mrp,
            product_image=product_image 

        )

        messages.success(request, "Product added successfully!")
        return redirect("manage_products")

    return redirect("manage_products")



def edit_material(request, pk):
    material = get_object_or_404(Inventory, pk=pk)

    if request.method == "POST":
        material.product_name = request.POST.get("product_name")
        category_id = request.POST.get("product_category")
        subcategory_id = request.POST.get("product_subcategory")
        vendor_id = request.POST.get("vendor")
        material.quantity = request.POST.get("quantity")
        material.price_per_unit = request.POST.get("vendor_price")
        material.mrp = request.POST.get("mrp")

        # Fetch related models
        material.product_category = get_object_or_404(Category, id=category_id)
        material.product_subcategory = get_object_or_404(SubCategory, id=subcategory_id)
        material.vendor = get_object_or_404(Vendor, id=vendor_id)

        # Handle product image update
        if "product_image" in request.FILES:
            material.product_image = request.FILES["product_image"]

        material.save()
        messages.success(request, "Product updated successfully!")
        return redirect("manage_products")

    return redirect("manage_products")  # Redirect in case of GET request

def delete_material(request, pk):
    material = get_object_or_404(Inventory, pk=pk)

    # Delete image file from the media folder if it exists
    if material.product_image:
        image_path = material.product_image.path
        if os.path.isfile(image_path):
            os.remove(image_path)

    # Now delete the Inventory record
    material.delete()

    return redirect("manage_products")
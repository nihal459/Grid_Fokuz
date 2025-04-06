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

def sales_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if (user.is_staff or user.is_admin) and not user.is_superuser:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Access denied. Only staff or admin users are allowed.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'sales_login.html')




def register_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, password=password)
            user.is_admin = True
            user.save()
            messages.success(request, "Admin created successfully.")

        return redirect('register_admin')

    return render(request, 'register_admin.html')



def sales_logout(request):
    logout(request)
    return redirect('sales_login') 



from django.db.models import Sum

def index(request):
    total_vendors = Vendor.objects.count()
    total_products = Inventory.objects.count()

    # Categorize products by Vendor
    products_by_vendor = Inventory.objects.values('vendor__name').annotate(count=models.Count('id'))

    # Categorize products by Category
    products_by_category = Inventory.objects.values('product_category__name').annotate(count=models.Count('id'))

    # Categorize products by SubCategory
    subcategory_data = Inventory.objects.values('product_subcategory__name').annotate(count=models.Count('id'))

    context = {
        'total_vendors': total_vendors,
        'total_products': total_products,
        'products_by_vendor': products_by_vendor,
        'products_by_category': products_by_category,
        'subcategory_data': subcategory_data,
    }
    return render(request, 'index.html', context)
 


def manage_vendors(request):
    query = request.GET.get('q', '').strip()  # Get search query from request
    vendors = Vendor.objects.all()

    if query:
        vendors = vendors.filter(
            name__icontains=query  # Search by vendor name
        ) | vendors.filter(
            code__icontains=query  # Search by vendor code
        )

    return render(request, 'manage_vendors.html', {'salesmen': vendors, 'query': query})


def add_vendor(request):
    if request.method == 'POST':
        name = request.POST.get('vendor_name')
        code = request.POST.get('vendor_code')

        if Vendor.objects.filter(name=name).exists() or Vendor.objects.filter(code=code).exists():
            messages.error(request, "Vendor with this name or code already exists.")
            return redirect("manage_vendors")

        Vendor.objects.create(name=name, code=code)
        messages.success(request, "Vendor added successfully.")
        return redirect("manage_vendors")

    return redirect("manage_vendors")


def edit_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == "POST":
        vendor_name = request.POST.get("vendor_name").strip()
        vendor_code = request.POST.get("vendor_code").strip()

        # Check for uniqueness
        if Vendor.objects.exclude(id=vendor.id).filter(name__iexact=vendor_name).exists():
            messages.error(request, "Vendor name already exists!")
        elif Vendor.objects.exclude(id=vendor.id).filter(code__iexact=vendor_code).exists():
            messages.error(request, "Vendor code already exists!")
        else:
            vendor.name = vendor_name
            vendor.code = vendor_code
            vendor.save()
            messages.success(request, "Vendor updated successfully!")
            return redirect("manage_vendors")

    return redirect("manage_vendors")


def delete_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.delete()
    messages.success(request, "Vendor deleted successfully!")
    
    return redirect("manage_vendors")



from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect

User = get_user_model()

def manage_staffs(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = True
            user.save()
            messages.success(request, "Staff added successfully.")

        return redirect('manage_staffs')

    staffs = User.objects.filter(is_staff=True, is_superuser=False)
    return render(request, 'manage_staffs.html', {'staffs': staffs})


def delete_staff(request, staff_id):
    staff = get_object_or_404(User, id=staff_id)

    if staff.is_staff and not staff.is_superuser:
        staff.delete()
        messages.success(request, "Staff deleted successfully.")
    else:
        messages.error(request, "Cannot delete this user.")

    return redirect('manage_staffs')
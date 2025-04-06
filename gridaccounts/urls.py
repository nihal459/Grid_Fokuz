from django.urls import path
from . import views

urlpatterns = [ 
    
    path('', views.sales_login, name='sales_login'),
    path('sales_login', views.sales_login, name='sales_login'),
    path('sales_logout', views.sales_logout, name='sales_logout'),
    path('manage_staffs', views.manage_staffs, name='manage_staffs'),
    path('delete-staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('register_admin', views.register_admin, name='register_admin'),

    path('index', views.index, name='index'),
    path('manage_vendors/', views.manage_vendors, name='manage_vendors'),
    path('add_vendor/', views.add_vendor, name='add_vendor'),
    path('edit-vendor/<int:vendor_id>/', views.edit_vendor, name='edit_vendor'),
    path('delete-vendor/<int:vendor_id>/', views.delete_vendor, name='delete_vendor'),


]
from django.urls import path
from . import views

urlpatterns = [ 
    path('manage_category', views.manage_category, name='manage_category'),
    path('edit_category<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category<int:category_id>/', views.delete_category, name='delete_category'),

    path('manage_subcategory', views.manage_subcategory, name='manage_subcategory'),
    path('edit-subcategory/<int:subcategory_id>/', views.edit_subcategory, name='edit_subcategory'),
    path('delete-subcategory/<int:subcategory_id>/', views.delete_subcategory, name='delete_subcategory'),

    path("manage_products", views.manage_products, name="manage_products"),
    path("add_material", views.add_material, name="add_material"),
    path("edit_material/<int:pk>/", views.edit_material, name="edit_material"),
    path("delete_material/<int:pk>/", views.delete_material, name="delete_material"),


]
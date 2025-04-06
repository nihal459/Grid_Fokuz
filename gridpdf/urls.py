from django.urls import path
from . import views

urlpatterns = [

    path('invoice', views.invoice, name='invoice'),
    path("remove_product/<int:product_id>/", views.remove_product, name="remove_product"),
    path('generate-cart-pdf/', views.generate_cart_pdf, name='generate_cart_pdf'),
    path('search-products/', views.search_products, name='search_products'),
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path("update-cart-item/", views.update_cart_item, name="update_cart_item"),
]
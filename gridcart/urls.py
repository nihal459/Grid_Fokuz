from django.urls import path
from . import views

urlpatterns = [
    

    path('add_product_to_pdf/<int:product_id>/', views.add_product_to_pdf, name='add_product_to_pdf'),
    path('empty_whole_cart', views.empty_whole_cart, name='empty_whole_cart'),
    path("filter-pdf/", views.filter_pdf, name="filter_pdf"), 

]
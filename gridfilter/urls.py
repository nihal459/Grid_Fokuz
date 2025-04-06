from django.urls import path
from . import views

urlpatterns = [

    path('search-salesmen/', views.search_salesmen, name='search_salesmen'),
    path("filter-products/", views.filter_products, name="filter_products"),
    # path("filter-pdf/", views.filter_pdf, name="filter_pdf"), 

]
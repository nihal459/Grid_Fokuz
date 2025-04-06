from django.urls import path
from . import views

urlpatterns = [
    

    path("combo_pdf/", views.combo_pdf, name="combo_pdf"), 
    path('combo/step2/', views.combo_step2, name='combo_step2'),
    path('combo/step3/', views.combo_step3, name='combo_step3'),
    path('combo/step4/', views.combo_step4, name='combo_step4'),
    path('combo/generate/', views.generate_combos, name='generate_combos'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart3, name='add_to_cart3'),
    path('add-whole-combo-to-cart/', views.add_whole_combo_to_cart, name='add_whole_combo_to_cart'),
]
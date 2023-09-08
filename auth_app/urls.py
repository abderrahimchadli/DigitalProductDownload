from django.contrib import admin
from django.urls import path ,include
from . import views

    

urlpatterns = [
  path('', views.home, name='post_list'),
  path('license-key/', views.license_key, name='license_key'),

  path("get-product/", views.getproduct),
  path("get-files/", views.getfiles),

  #dp =digital product
  path('dipr-form-submit/', views.dp_form_submit, name='dp_form_submit'),
  path('product_submit/', views.product_submit, name='product_submit'),

  
  path('save-file/', views.save_file, name='save_file'),

     #jason response
    #path("activate/",views.activate_billing),
  path("handle-charge/<int:id>",views.handle_billing),
  path("activate-plan/<int:id>",views.activate_plan),
  path("pricing/",views.pricing),
  #path('get_serial_keys/', views.get_serial_keys, name='get_serial_keys'),
  path('get_digital_product/', views.get_digital_product, name='get_digital_product'),
  path('get_variants_for_digital_product/', views.get_variants_for_digital_product, name='get_variants_for_digital_product'),
  path('edit-digital-product/', views.edit_digital_product, name='edit-digital-product'),


 ]

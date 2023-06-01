from django.contrib import admin
from django.urls import path ,include
from . import views

    

urlpatterns = [
  path('', views.home, name='post_list'),
  path("search-product/", views.getproduct),
  #dp =digital product
  path('dipr-form-submit/', views.dp_form_submit, name='dp_form_submit'),

     #jason response
    #path("activate/",views.activate_billing),
  path("handle-charge/<int:id>",views.handle_billing),
  path("activate-plan/<int:id>",views.activate_plan),
  path("pricing/",views.pricing),
 ]

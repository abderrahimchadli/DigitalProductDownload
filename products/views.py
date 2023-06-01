from django.shortcuts import render
import shopify 
from shopify_auth.decorators import login_required
from django.shortcuts import redirect
# Create your views here.
from django.core import serializers
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponse,JsonResponse

# Create your views here.





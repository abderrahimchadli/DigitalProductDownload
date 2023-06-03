from django.db import models

# Create your models here.
# auth_demo/auth_app/models.py
from shopify_auth.models import AbstractShopUser

class AuthAppShopUser(AbstractShopUser):
    pass

class Billing(models.Model):
    user=models.IntegerField()
    charge_id=models.TextField(max_length=50,null=True,unique=True)
    created_at=models.DateTimeField()
    current_period_end=models.DateTimeField(null=True)
    trial_ends_on=models.DateTimeField(null=True)
    
class Plan(models.Model):
    name=models.TextField(null=True)
    price=models.FloatField()
    trial_days=models.IntegerField()
    
class Customer(models.Model):
    name = models.CharField(max_length=100)
    useri=models.ForeignKey(AuthAppShopUser ,on_delete=models.CASCADE)
    email = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
  

class DigitalProduct(models.Model):
    product_id= models.TextField()
    product_title=models.TextField()
    userid=models.ForeignKey(AuthAppShopUser ,on_delete=models.CASCADE)
    has_file=models.BooleanField(default=False)
    has_url=models.BooleanField(default=False)
    isall=models.BooleanField(default=True)
    
class Variant(models.Model):
    product = models.ForeignKey(DigitalProduct, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='digital_product_files/')
    sku = models.TextField()
    has_serial_keys = models.BooleanField(default=False)
    
class SerialKey(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    is_used = models.BooleanField(default=False)
    
class DownloadLink(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    serial_key = models.ForeignKey(SerialKey, on_delete=models.CASCADE, null=True)
    is_valid = models.BooleanField(default=True)
    size=models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_update=models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    order_id=models.TextField()
    order_name=models.TextField()
    product=models.ForeignKey(DigitalProduct, on_delete=models.CASCADE)
    variant=models.ForeignKey(Variant, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity=models.TextField()

class OrderKeys(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE ,null=True)
    serial_key = models.ForeignKey(SerialKey, on_delete=models.CASCADE, null=True)


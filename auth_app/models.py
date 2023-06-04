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
    
class DigitalProduct(models.Model):
    shopify_id= models.IntegerField(unique=True)
    title=models.TextField()
    user=models.ForeignKey(AuthAppShopUser ,on_delete=models.CASCADE)
    
class Variant(models.Model):
    shopify_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    product = models.ForeignKey(DigitalProduct, on_delete=models.CASCADE)

    
class File(models.Model):
    name=models.TextField(default=None,null=True)
    url=models.TextField(default=None,null=True)
    type=models.CharField(max_length=20, choices=(('FILE', 'file'),('URL', 'url'),('NONE', 'none'),))
    size=models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update=models.DateTimeField(auto_now_add=True)
    additional_note=models.TextField(default=None,null=True)

class VariantFile(models.Model):
    variant = models.ForeignKey(Variant,on_delete=models.CASCADE)
    file = models.ForeignKey(File,on_delete=models.CASCADE)



class SerialKey(models.Model):
    key = models.CharField(max_length=255)
    usage_limit = models.IntegerField(default=0)
    usage_count = models.IntegerField(default=0)
    file = models.ForeignKey(File,on_delete=models.CASCADE)


class Order(models.Model):
    order_id=models.TextField()
    order_name=models.TextField()
    product=models.ForeignKey(DigitalProduct, on_delete=models.CASCADE)
    variant=models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity=models.TextField()

class OrderKeys(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE ,null=True)
    serial_key = models.ForeignKey(SerialKey, on_delete=models.CASCADE, null=True)


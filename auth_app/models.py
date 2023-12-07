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
    shopify_id= models.IntegerField()
    image_url=models.TextField(default=None,null=True)
    title=models.TextField()
    user=models.ForeignKey(AuthAppShopUser ,on_delete=models.CASCADE)
    used_files_ids= models.TextField(max_length=2000) #"id1,id2,id3..idn"  42382585004184
    used_variants_ids= models.TextField(max_length=2000) #"id1,id2,id3..idn" 
    


    
    
    def get_used_variant_names(self):
        
        # Split the used variant IDs string into a list of IDs
        variant_ids = self.used_variants_ids.split(',')

        # Query the Variant model to get the names of the used variants
        used_variant_names = Variant.objects.filter(shopify_id__in=variant_ids).values_list('name', flat=True)

        return used_variant_names


    def get_variant_ids_by_names(self, variant_names):
        # Query the Variant model to get the IDs of the variants with the given names
        variant_ids = Variant.objects.filter(name__in=variant_names).values_list('shopify_id', flat=True)

        return variant_ids

    def get_used_file_ids(self):
        # Split the used file IDs string into a list of IDs
        file_ids = self.used_files_ids.split(',')

        return file_ids

    def get_used_file_names(self):
        # Split the used file IDs string into a list of IDs
        file_ids = self.used_files_ids.split(',')

        # Query the File model to get the names of the used files
        used_file_names = File.objects.filter(id__in=file_ids).values_list('name', flat=True)

        return used_file_names
    
    def get_serial_keys(self):
        # Query the SerialKey model to get the keys associated with this DigitalProduct
        serial_keys = SerialKey.objects.filter(digital_product=self)

        return serial_keys
    
    def get_used_variant_ids(self):
        # Split the used variant IDs string into a list of IDs
        variant_ids = self.used_variants_ids.split(',')
        
        return variant_ids

    

    
class Variant(models.Model):
    shopify_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)


class File(models.Model):
    name=models.TextField(default=None,null=True)
    url=models.TextField(default=None,null=True)
    type=models.CharField(max_length=20, choices=(('FILE', 'file'),('URL', 'url'),('NONE', 'none'),))
    size=models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    additional_note=models.TextField(default=None,null=True)


class DigitalProductFile(models.Model):
    digital_product = models.ForeignKey(DigitalProduct,on_delete=models.CASCADE)
    file = models.ForeignKey(File,on_delete=models.CASCADE)


class SerialKey(models.Model):
    key = models.CharField(max_length=255)
    usage_limit = models.IntegerField(default=0)
    usage_count = models.IntegerField(default=0)
    digital_product = models.ForeignKey(DigitalProduct, on_delete=models.CASCADE)


class Order(models.Model):
    order_id=models.TextField()
    order_name=models.TextField()
    product=models.ForeignKey(DigitalProduct, on_delete=models.CASCADE)
    variant=models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity=models.TextField()
    has_download = models.BooleanField(default=False)
    download_url = models.URLField(blank=True, null=True)



class OrderKeys(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE ,null=True)
    serial_key = models.ForeignKey(SerialKey, on_delete=models.CASCADE, null=True)


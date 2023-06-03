from django.shortcuts import render
import shopify , os, json, requests
from shopify_auth.decorators import login_required
from django.shortcuts import redirect
from .models import Plan
# Create your views here.
from django.core import serializers
from .models import Billing ,Plan,Customer,DigitalProduct,Variant,SerialKey,DownloadLink,Order,OrderKeys
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponse,JsonResponse


@login_required
def check_user_billing(request):
    if request.user.is_authenticated:
        with request.user.session:
            userbilling=Billing.objects.filter(user=request.user.id).order_by('-id').first()
            if userbilling:
                try:
                    user_charge=shopify.RecurringApplicationCharge.find(userbilling.charge_id)
                    if user_charge.status == 'active':
                        return True
                except Exception as e:
                    request.session.flush()
                    create_file = open("requestlogs", "a")
                    create_file.write("usercharge error"+'\n')
                    create_file.close()
                    return -1
    return False


@login_required
def home(request, *args, **kwargs):
    if request.GET.get('shop') != None:
        shop = request.GET.get('shop')
        if shop != request.user.myshopify_domain:
            logout(request)
            request.session.flush()
            return redirect(f"/?shop={shop}")
    checkbilling = check_user_billing(request)
    if checkbilling == True:
        return render(request, "home.html")
    if checkbilling == -1:
        return redirect(settings.LOGIN_REDIRECT_URL)
    return redirect(activate_plan)


@login_required
def activate_plan(request, id):
    plan=Plan.objects.filter(id=id)
    if not plan :
        return JsonResponse (data={"error":"not found"})
    
    plan = plan[0]
    
    print(type(plan.trial_days))
    with request.user.session:
         application_charge = shopify.RecurringApplicationCharge.create({
            'name': f'{plan.name} plan',
            'price': plan.price,
            'test': True,
            'return_url': f'{settings.APP_URL}/handle-charge/{plan.id}',
            'trial_days':plan.trial_days
            }
        )    
        
    return redirect(application_charge.confirmation_url)
    """
    if check_user_billing(request) != False:
        return redirect(home)
    
    with request.user.session:
        application_charge = shopify.RecurringApplicationCharge.create(
            {
                                'name': 'Digital Product Download plan',
                                'price': 9.99,
                                'test': True,
                                'return_url': f'{settings.APP_URL}/handle-charge',
                                'trial_days': 1    
                                }
            
            )

        return redirect(application_charge.confirmation_url)

    """

        
@login_required        
def handle_billing(request, id):
    if request.method != 'GET' or 'charge_id' not in request.GET:
        return render(request,"error-403.html")
    
    plan=Plan.objects.filter(id=id)
    if not plan :
        return JsonResponse (data={"error":"not found"})
    
    plan = plan[0]
    
    charge_id=request.GET['charge_id']
    with request.user.session:
        activated_charge = shopify.RecurringApplicationCharge.find(charge_id)
        has_been_billed = activated_charge.status == 'active'
        if has_been_billed:
            user_billings=Billing.objects.filter(user=request.user.id)
            for usbil in user_billings:
                shopify.RecurringApplicationCharge.delete(usbil.charge_id)
                Billing.objects.filter(id=usbil.id).delete()
            p = Billing(user=request.user.id,charge_id=activated_charge.id, created_at=activated_charge.created_at,current_period_end=activated_charge.billing_on,trial_ends_on=activated_charge.trial_ends_on)
            p.save()

            
            return redirect(home)

@login_required
def pricing(request):
    
    return render(request,"pricing.html")






def error_404_view(request, exception):
       
    # we add the path to the the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, 'error-404.html')


def logoutview(request):
    logout(request)
    return redirect(home)

def getproduct(request, *args, **kwargs):
    jsproducts=[]
    with request.user.session:
        products = shopify.Product.find()
        for product in products:
            
            jsproducts.append(product.to_dict())
        
    print(jsproducts)        
    rsp_obj = {'products': jsproducts}

    return JsonResponse({"status":True,"msg":"",'data':rsp_obj})

def getproduct(request, *args, **kwargs):
    jsproducts=[]
    with request.user.session:
        products = shopify.Product.find()
        for product in products:
            
            jsproducts.append(product.to_dict())
        
    print(jsproducts)        
    rsp_obj = {'products': jsproducts}

    return JsonResponse({"status":True,"msg":"",'data':rsp_obj})


        



from django.core.exceptions import ValidationError
from django.db import transaction
from django.views.decorators.http import require_POST
from django.core.files.storage import FileSystemStorage

from google.cloud import storage

@login_required
@require_POST
def dp_form_submit(request):
    try:
        with transaction.atomic():
            # Extract form data
            #print(request.POST)
            dp_type = request.POST.get('dp-type')
            product_id = request.POST.get('product_id')
            product_title = request.POST.get('product_title')
            has_serial_keys = request.POST.get('checkkeys') == 'on'
            has_file = request.POST.get('dp-type') == 'file'
            has_url=request.POST.get('dp-type') == 'url'
            variants = request.POST.get('variants')
            variants = json.loads(variants)
            print(variants)
            #print(type(variants))
            #product_sku = request.POST.get('variantsku')
            #print(type(product_sku))
            #variant_name = request.POST.get('variantname')
            variant_file = request.FILES.get('dp-file')
            variant_has_serial_keys = request.POST.get('licensekeys') == 'Generatenewlicense'
            #print(variant_has_serial_keys)
            serial_keys = request.POST.get('generatedkeys')
            url=request.POST.get('external-URL')
            #print(url)
            # Validate form data
            if not all([dp_type, product_id, product_title, product_sku]):
                raise ValidationError('Missing required fields')
            if has_serial_keys and not serial_keys:
                raise ValidationError('Serial keys are required for variants with serial keys')
                        # Check file size
            if variant_file and variant_file.size > 50 * 1024 * 1024:  # 50 MB
                return JsonResponse({'success': False, 'message': 'File size is too large. Maximum file size is 50 MB.'})
            if has_url and not url:
                    return JsonResponse({'success': False, 'message': 'URL is required for variants with URL '})


                
            print(has_serial_keys)
            # Create digital product
            
            digital_product = DigitalProduct.objects.create(
                product_id=product_id,
                product_title=product_title,
                has_serial_keys=has_serial_keys,
                has_url=has_url,
                has_file=has_file,
                productSKU=product_sku,
                userid=request.user,
            )
            
            if has_url:
                    variant = Variant.objects.create(
                    product=digital_product,
                    name=variant_name,
                    file=url,
                    
                    
                    has_serial_keys=variant_has_serial_keys,
                )
                
            # Save variant file to server
            if variant_file:
                #filename = os.path.join(settings.MEDIA_ROOT, variant_file.name)
                #with open(filename, 'wb+') as f:
                #    for chunk in variant_file.chunks():
                #        f.write(chunk)
                fs = FileSystemStorage(location='digital_product_files')
                filename = fs.save(variant_file.name, variant_file)
                variant_file_path = fs.url(filename)
                digital_product.file_url = variant_file_path
                saved_file =digital_product.save()

                #file_path = os.path.join(settings.MEDIA_ROOT, filename)

                file_path = os.path.abspath(os.path.join('digital_product_files/', filename))

                print(file_path)
                

                # Set the path to your service account key JSON file    
                credentials_path = 'K:\PROJECTS\DigitalProductDownload\my-project-key.json'

                # Initialize the client
                client = storage.Client.from_service_account_json(credentials_path)

                storage_client = storage.Client.from_service_account_json('K:\PROJECTS\DigitalProductDownload\my-project-key.json')
                bucket_name = 'bucketfilename'
                blob_name = f'variants/{filename}'
                bucket = storage_client.bucket(bucket_name)
                if not bucket.exists():
                    bucket.create()
                    
                blob = bucket.blob(blob_name)
                with open(file_path, 'rb') as file:
                    blob.upload_from_file(file)
                
                digital_product.file_url = blob.public_url
                digital_product.save()
                blob.make_public()
                print(digital_product.file_url)
                variant_file=digital_product.file_url

                variant = Variant.objects.create(
                    product=digital_product,
                    name=variant_name,
                    file=variant_file,
                    
                    
                    has_serial_keys=variant_has_serial_keys,
                )


            # Create variant if specified
            if variant_name:
                print(variant_has_serial_keys)
                print(serial_keys)
                # Add serial keys if specified
                if variant_has_serial_keys and serial_keys:
                    
                    keys = serial_keys.split('\n')
                    print(keys)
                    for key in keys:
                        key = key.strip()  # Remove leading/trailing whitespace
                        if key:
                            SerialKey.objects.create(variant=variant, key=key)
                            
            response_data = {'success': True}
    except Exception as e:
        response_data = {'success': False, 'message': str(e)}
        
    return JsonResponse(response_data)
@login_required
def license_key(request):
    return render(request, 'license-key.html')


@login_required
def get_serial_keys(request):
    # Retrieve all serial keys
    serial_keys = SerialKey.objects.all()

    # Prepare the serial keys data
    keys_list = []
    for key in serial_keys:
        keys_list.append({
            'id': key.id,
            'variant': key.variant.name,
            'product': key.variant.product.product_title,
            'key': key.key,
            'is_used': key.is_used,
        })

    return JsonResponse({"status":True,'data':keys_list})



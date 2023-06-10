from django.shortcuts import render
import shopify , os, json, requests
from shopify_auth.decorators import login_required
from django.shortcuts import redirect
from .models import Plan
# Create your views here.
from django.core import serializers
from .models import Billing ,Plan,DigitalProduct,Variant,SerialKey,File
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
    print(checkbilling)
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
#new app working ---- send data to frontend
def getproduct(request, *args, **kwargs):
    


    jsproducts=[]
    with request.user.session:
        products = shopify.Product.find()
        for product in products:
            
            jsproducts.append(product.to_dict())
    
        
    #print(jsproducts)        
    rsp_obj = {'products': jsproducts}

    return JsonResponse({"status":True,"msg":"",'data':rsp_obj})

def getfiles(request,*args,**kwargs):

    files = File.objects.all()
    file_data = []
    for file in files:
        file_data.append({
            'id': file.id,
            'name': file.name,
            'url': file.url,
            'type': file.type,
            'size': file.size,
            'created_at': file.created_at,
            'updated_at': file.updated_at,
            'additional_note': file.additional_note,
        })
    response = {'files':file_data}

    return JsonResponse({"status":True,"msg":"",'data':response})

#def getproduct(request, *args, **kwargs):
#    jsproducts=[]
#    with request.user.session:
#        products = shopify.Product.find()
#        for product in products:
#            
#            jsproducts.append(product.to_dict())
#        
#    #print(jsproducts)        
#    rsp_obj = {'products': jsproducts}
#
#    return JsonResponse({"status":True,"msg":"",'data':rsp_obj})













from django.core.exceptions import ValidationError
from django.db import transaction
from django.views.decorators.http import require_POST
from django.core.files.storage import FileSystemStorage

from google.cloud import storage

@login_required
@require_POST
#upload file to database
def save_file(request):
    if request.method == 'POST':
        
        if request.POST.get('filename') == '' :
            return JsonResponse({'success': False, 'message': 'File name is required'})
        
        if  'file' not in request.FILES and 'url' not in request.POST:
            return JsonResponse({'success': False, 'message': 'a file or url is required '})
        
        
        
        link_url = ""
        filesize = 0
        filename = request.POST.get('filename')
        
        if request.POST.get('url'):
            link_url = request.POST.get('url')
        
        

        if 'file' in request.FILES:
            if request.FILES['file'].size > 50 * 1024 * 1024:
                return JsonResponse({'success': False, 'message': 'File size is too large. Maximum file size is 50 MB.'})
            
            file = request.FILES['file']
            
            fs = FileSystemStorage(location='digital_product_files')
            file_name = fs.save(file.name, file)
            file_path = os.path.abspath(os.path.join('digital_product_files/', file_name))
            
            extension=os.path.splitext(file_path)[-1]
            storage_client = storage.Client.from_service_account_json('K:\PROJECTS\DigitalProductDownload\my-project-key.json')
            bucket_name = 'bucketfilename'
            blob_name = f'variants/File_{filename}_{request.user.myshopify_domain}{extension}'
            bucket = storage_client.bucket(bucket_name)
            if not bucket.exists():
                bucket.create()
                
            blob = bucket.blob(blob_name)
            with open(file_path, 'rb') as file:
                blob.upload_from_file(file)
                
            blob.make_public()
            print(blob.size)
            filesize = blob.size
            link_url = blob.public_url
            filename = filename + extension
            os.remove(file_path)

            
        created_file = File.objects.create(name=filename,url=link_url,size=filesize)            


        
        return JsonResponse({'success': True, 'message': 'File saved successfully, and reloaded to the file list.'}) if created_file else JsonResponse({'success': False, 'message': 'Error saving file.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request.'})
    
import urllib.parse

@login_required
@require_POST
def product_submit(request):
    try:
        with transaction.atomic():
            product_id=request.POST.get('selected-product')
            product_title=request.POST.get('product-title')
            variants=request.POST.getlist('variant')
            filid=request.POST.get('files')
            licensekey=request.POST.get('licensekeys')
            Keyswitcher=request.POST.get('Keyswitcher')
            variants = [(urllib.parse.unquote(variant)) for variant in variants]
            
            if not  product_id:
                raise ValidationError('Missing product fields')

            if not variants :
                raise ValidationError('Missing variants fields')
            
            digital_product = DigitalProduct.objects.update_or_create(
                shopify_id=product_id,
                defaults={'title': product_title, 'user':request.user}
            )
            assigned_variants = []

            for v in variants:
                v = json.loads(v)
                     
                variant = Variant.objects.update_or_create(
                        shopify_id=v['id'],
                        
                        defaults={'name':v['title'],'sku':v['sku'],'digital_product':digital_product}
                    )
                assigned_variants.append(variant)

            response_data = {'success': True}

    except Exception as e:
        response_data = {'success': False, 'message': str(e)}
    return JsonResponse(response_data)
#
#



@login_required
@require_POST
def dp_form_submit(request):
    try:
        with transaction.atomic():
            # Extract form data
            
            dp_type = request.POST.get('dp-type')
            product_id = request.POST.get('product_id')
            product_title = request.POST.get('product_title')
            has_serial_keys = request.POST.get('checkkeys') == 'on'
            file_type = request.POST.get('dp-type') #'file'/'url'
            variants = json.loads(request.POST.get('variants'))
            file = request.FILES.get('dp-file')
            url=request.POST.get('external-URL')
            variant_has_serial_keys = request.POST.get('licensekeys') == 'Generatenewlicense' ##
            serial_keys = request.POST.get('generatedkeys')
            manual_keys=request.POST.get('manualkeys')
            print(manual_keys)
            file_name=request.POST.get('filename')
            url_file_name=request.POST.get('urlfilename')
            usage_limit=request.POST.get('usage-limit')
            description=request.POST.get('additional-note')
            # Validate form data
            if not all([dp_type, product_id, product_title,file_type,variants]):
                raise ValidationError('Missing required fields')
            
            if dp_type == 'file' and not file:
                raise ValidationError('File not selected.')
                
            if has_serial_keys and not (serial_keys or manual_keys):
                raise ValidationError('Serial keys are required for variants with serial keys')
            
            # Check file size
            if file and file.size > 50 * 1024 * 1024:  # 50 MB
                return JsonResponse({'success': False, 'message': 'File size is too large. Maximum file size is 50 MB.'})
            
            if file_type == 'url' and not url:
                return JsonResponse({'success': False, 'message': 'URL is required for variants with URL '})

            
            if not serial_keys:
                serial_keys=manual_keys
                

            # Create digital product
            digital_product, created = DigitalProduct.objects.update_or_create(
                shopify_id=product_id,
                defaults={'title': product_title, 'user':request.user}
            )
            

            assigned_variants = []
            for v in variants:
                print(v)
                variant, created = Variant.objects.update_or_create(
                    shopify_id=v['id'],
                    defaults={'name':v['title'],'sku':v['sku'],'product':digital_product}
                )
                assigned_variants.append(variant)
            
            link_url = ''
            filesize = 0
            digital_filename = ''
            
            if file_type == 'url':
                link_url = url
                filesize = 0
                digital_filename = url_file_name
                
            elif file_type == 'file':
                fs = FileSystemStorage(location='digital_product_files')
                filename = fs.save(file.name, file)
                file_path = os.path.abspath(os.path.join('digital_product_files/', filename))
                
                extension=os.path.splitext(file_path)[-1]
                storage_client = storage.Client.from_service_account_json('K:\PROJECTS\DigitalProductDownload\my-project-key.json')
                bucket_name = 'bucketfilename'
                blob_name = f'variants/File_{file_name}_{request.user.myshopify_domain}_{product_id}{extension}'
                bucket = storage_client.bucket(bucket_name)
                if not bucket.exists():
                    bucket.create()
                    
                blob = bucket.blob(blob_name)
                with open(file_path, 'rb') as file:
                    blob.upload_from_file(file)
                    

                blob.make_public()
                print(blob.size)
                filesize = blob.size
                link_url = blob.public_url
                digital_filename = file_name + extension
                
                os.remove(file_path)

            
            created_file = File.objects.create(name=digital_filename,url=link_url,type=file_type,size=filesize,additional_note=description)

            
            
            #for variant in assigned_variants:
                #VariantFile.objects.create(variant=variant,file=created_file)
            
            if variant_has_serial_keys and serial_keys:    
                keys = serial_keys.split('\n')
                for key in keys:
                    key = key.strip()  # Remove leading/trailing whitespace
                    if key:
                        SerialKey.objects.create(file=created_file, key=key,usage_limit=usage_limit)
            
                
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



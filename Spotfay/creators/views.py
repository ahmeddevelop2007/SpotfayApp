from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, get_user_model 
from Authentications.models import Userinfos
# from creators.models import ....
from creators import views as creators_views
from brands import views as brands_views
from Authentications import views as authentications_views
from django.db.models import Q
from brands import models as brands_data
from Authentications import models as auth_data
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from .models import PaymentInfo, CreatorsProfits, AvailableEarnings
from django.template.loader import render_to_string
from decimal import Decimal as decimal



# Create your views here.
@login_required
def creators_offers(request):
    all_data = brands_views.getting_all_data(request)
    userinfos, created = Userinfos.objects.get_or_create(user=request.user)
    user = request.user
    

    # available_jobs = brands_views.VideoOrderDetails.objects.exclude(Q(selecting_creators__in=[request.user.id]) | Q(order_status__in=['completed', 'processing', 'cancelled'])).order_by('-id')[:2]
    exclude_fields = ['telegram_account'] # add the excluded fields here

    if request.method == 'POST':
        fields_checked = check_fields(userinfos, exclude_fields)
        if not fields_checked:
            messages.error(request, "Please, complete your profile first to be able to apply this job!")
            print("complete the fields first")
        else:
            try:
                job_id = request.POST.get('job_id')
                job = brands_data.VideoOrderDetails.objects.get(id=job_id)
                brand = job.user
                job.selecting_creators.add(request.user.id)
                job.order_status = 'pending_creator_approval'
                job.save()
                subject = f"Creator Applied on your project {job.project_name}"
                message = f"""Dear {brand.first_name} {brand.last_name},

Your project {job.project_name} has been selected by the creator {request.user.first_name} {request.user.last_name}

Click here to view your order 
127.0.0.1:8000/brands/order/{job_id}/

Best regards,
Spotfay
{settings.SITE_LINK}
spotfaymarketing@gmail.com"""
                from_email = settings.EMAIL_HOST_USER
                to_email = brand.email
                try:
                    send_mail(subject, message, from_email, [to_email])
                except:
                    print("Error sending email")
            except KeyError:
                return redirect('creators_offers')
    
   
    context = {
        'userinfos':userinfos,
        'user':user, 
    }
    context.update(all_data)
    return render(request, 'creators_offers.html', context)

def check_fields(userinfos, exclude_fields):
    """
    Check if all fields except exclude_fields are filled with information.

    Args:
        userinfos (object): The object containing user information.
        exclude_fields (list): A list of fields to exclude from the check.

    Returns:
        bool: True if all fields are filled, False otherwise.
    """
    for field in userinfos.__dict__:
        if field not in exclude_fields and not userinfos.__dict__[field]:
            return False
    return True

@login_required
def load_more_jobs(request):
    page = int(request.GET.get('page', 1))
    jobs_per_page = 7
    offset = (page - 1) * jobs_per_page

    jobs = brands_views.VideoOrderDetails.objects.exclude(Q(selecting_creators__in=[request.user.id]) | Q(order_status__in=['completed', 'processing', 'cancelled'])).order_by('-id')[offset:offset + jobs_per_page]
    
    has_more = jobs.count() > 0
    jobs_html = ''
    for job in jobs:
        job_description = job.additional_notes
        job_description_class = 'd-block' if job_description else 'd-none'
        jobs_html += '''
        <button type="button" class="border-0 col-xxl-2 col-xl-3 col-lg-3 col-md-4 card-hover col-sm-6 col-12 bg-transparent p-sm-3 p-md-2 p-0 my-md-0 my-sm-0 my-2" data-bs-toggle="offcanvas" data-bs-target="#offer_details{job_id}">
            <div class="card shadow-sm rounded rounded-1 border-0">
            <div class="d-flex align-items-center justify-content-center rounded rounded-1 overflow-hidden m-2">
                <img src="{product_img_url}" class="rounded rounded-1" style="height: 13rem;width:auto;" alt="...">
            </div>
            <h5 class="text-start ms-2">{project_name}</h5>
            <div class="card-body px-0">
                <div class="d-flex align-items-center justify-content-between px-2">
                <h6 class="fs-6 m-0 text-secondary">Videos</h6>
                <h6 class="fs-6 m-0">{num_of_videos} <!--<span class="text-secondary">/10</span>--></h6>
                </div>
                <hr class="mx-2 mt-0">
                <div class="d-flex align-items-center justify-content-between px-2">
                <h6 class="m-0 text-secondary">Earnings</h6>
                <span class="badge bg-color px-3 rounded-pill">{creators_price:.0f}$</span>
                </div>
                <div class="d-flex align-items-center justify-content-between mt-3 px-2">
                <h6 class="m-0 text-secondary">Product value</h6>
                <h6 class="m-0">{product_value}$</h6>
                </div>
            </div>
            </div>
        </button>
        <!-- offcanvas offer details -->
        <div class="offcanvas offcanvas-end" tabindex="-1" id="offer_details{job_id}" aria-labelledby="offcanvasright">
            <div class="offcanvas-header d-block d-md-none" dir="rtl">
            <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            </div>
            <div class="offcanvas-body px-0">
            <div class="first-section container">
            <img src="{product_img_url}" style="height: 16rem;" class="rounded col-12 col-lg-10" alt="">
            <!-- Brand -->
            <div class="d-flex align-items-center mt-2 gap-2">
                <div class="rounded-circle d-flex align-items-center justify-content-center profile-picture overflow-hidden" style="width:3.5rem;height:3.5rem;">
                <img src="{company_logo_url}" style="object-fit:cover;" class="w-100 h-100" alt="...">
                </div>
                <div class="">
                <h6 class="mb-1 text-secondary">Brand</h6>
                <h5 class="mb-0">{company_name}</h5>
                </div>
            </div>
            </div>
            <hr class="text-secondary fw-bold bg-secondary mx-0 mx-md-3" size="4px">
            <div class="second-section container ms-0 col-12 col-md-9">
            <h5 class="mb-3">{product_name}</h5>
            <div class="d-flex align-items-center justify-content-between">
                <h6 class="text-secondary">Earnings</h6>
                <h5>{creators_price:.0f}$</h5>
            </div>
            <div class="d-flex align-items-center justify-content-between">
                <h6 class="text-secondary">Product value</h6>
                <h6>{product_value}$</h6>
            </div>
            <a href="https://{product_link}" target="_blank" class="d-flex align-items-center gap-3 mt-2 text-decoration-none" style="color:rgb(17	102	253);">Product link <span class="material-symbols-outlined">arrow_outward</span></a>
            </div>
            <hr class="text-secondary fw-bold bg-secondary mx-0 mx-md-3" size="4px">
            <div class="third-section container ms-0 col-12 col-md-9">
            <h5 class="mb-3">Job details</h5>
            <div class="d-flex align-items-center justify-content-between">
                <h6 class="text-secondary">Video duration</h6>
                <h6>{video_duration} sec.</h6>
            </div>
            <div class="d-flex align-items-center justify-content-between">
                <h6 class="text-secondary">Content format</h6>
                <h6>{video_size}</h6>
            </div>
            <div class="d-flex align-items-center justify-content-between">
                <h6 class="text-secondary">Content type</h6>
                <h6>{video_type}</h6>
            </div>
            </div>
            <div>
                <hr class="text-secondary fw-bold bg-secondary mx-0 mx-md-3 {job_description_class}" size="4px">
                <div class="fourth-section container ms-0">
                <h5 class="mb-3">Job description</h5>
                <p class="text-secondary fs-6">{job_description}</p>
                </div>
            </div>
            <form method="POST" class="mt-5 d-flex justify-content-center">
            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
            <input type="hidden" name="job_id" value="{job_id}">
            <button type="submit" class="btn bg-color btn-primary fs-5 py-0 px-5 text-white">Apply</button>
            </form>
            </div>
        </div>
        '''.format(
            job_id=job.id,
            product_img_url=job.product_img.url,
            project_name=job.project_name,
            num_of_videos=job.num_of_videos,
            creators_price=job.creators_price,
            company_logo_url=job.company.company_logo.url,
            company_name=job.company.company_name,
            product_name=job.product_name,
            product_link=job.product_link,
            video_duration=job.video_duration,
            video_size=job.video_size,
            video_type=job.video_type,
            job_description=job_description,
            job_description_class=job_description_class,
            product_value=job.product_description,
            csrf_token=request.COOKIES['csrftoken']
        )
    return JsonResponse({'has_more': has_more, 'html': jobs_html})

@login_required
def creators_profile(request):
    all_data= brands_views.getting_all_data(request)
    user = request.user
    newuserinfo = Userinfos.objects.get(user=request.user)
    available_jobs = brands_views.VideoOrderDetails.objects.exclude(Q(selecting_creators=request.user.id) | Q(order_status='pending_approval')).order_by('-id')
    user_videos = brands_data.Video.objects.filter(user=newuserinfo, video_status='previous_works')
    left_videos = 4 - user_videos.count()

    if request.method == 'POST' and request.POST.get('form_type') == 'personal_info':
        profile_image = request.FILES.get('profile_image')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        birth_date = request.POST.get('birth-date')
        gender = request.POST.get('gender')
        userinfo = request.POST.get('userinfo')
        if profile_image:
            newuserinfo.user_profile = profile_image
            newuserinfo.save()
        if birth_date:
            newuserinfo.birthdate = birth_date
            newuserinfo.save()
        if userinfo:
            newuserinfo.userinfo = userinfo
            newuserinfo.save()
        newuserinfo.gender = gender
        newuserinfo.save()
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return redirect('creators_profile')

    if request.method == 'POST' and request.POST.get('form_type') == 'shipping_info':
        shipping_data = {
            'country': request.POST.get('country'),
            'city': request.POST.get('city'),
            'address': request.POST.get('address'),
            'postalcode': request.POST.get('postal_code'),
            'phonenum': request.POST.get('phone_no'),
            'insta_account': request.POST.get('insta_account'),
            'tiktok_account': request.POST.get('tiktok_account'),
            'telegram_account': request.POST.get('telegram_account')
        }
        for field_name, field_value in shipping_data.items():
            if field_value:
                print(field_name)  # Output: country, city, address, etc.
                newuserinfo.__dict__[field_name] = field_value
                newuserinfo.save()
        return redirect('creators_profile')
                      
    if request.method == 'POST' and request.POST.get('form_type') == 'previous_works':
        video_files = request.FILES.getlist('video_file')
        for  file in video_files:
            video = brands_data.Video(video_file=file, user=newuserinfo, video_status='previous_works')
            video.save()
        return redirect('creators_profile')

    if request.method == 'POST' and request.POST.get("form_type") == "email":
        email = request.POST.get("email")
        user.email = email
        user.save()
        return redirect(creators_settings)
    
    if request.method == 'POST' and request.POST.get("form_type") == "password":
        new_password = request.POST.get("new_password")
        user.set_password(new_password)
        user.save()
        return redirect(creators_settings)
    
        
    context = {
        'jobs':available_jobs,
        'userinfos':newuserinfo,
        'user':user,
        'previous_works':user_videos,
    }
    context.update(all_data)
    return render(request, 'creators_profile.html', context)

@login_required
def creators_deletevideo(request, video_id):
    video = brands_data.Video.objects.get(id=video_id)
    video.delete()
    return redirect('creators_profile') 

@login_required
def delete_video(request, order_id, video_id):
    video = brands_data.Video.objects.get(id=video_id)
    video.delete()
    return redirect('creators_orderdetails', order_id) 

@login_required
def creators_jobs(request):
    all_data = brands_views.getting_all_data(request)
    userinfos = Userinfos.objects.get(user=request.user)
    all_projects = brands_views.VideoOrderDetails.objects.filter(selecting_creators__in=[request.user.id])
    active_projects = brands_views.VideoOrderDetails.objects.filter(selecting_creators__in=[request.user.id], order_status__in=['pending_approval', 'processing'], applied_creator=userinfos)
    applied_projects = brands_views.VideoOrderDetails.objects.exclude(applied_creator__user=request.user).filter(selecting_creators__in=[request.user.id], order_status='pending_creator_approval')
    
    context = {
        'all_projects': all_projects,
        'active_projects': active_projects,
        'applied_projects': applied_projects,
        'userinfos': userinfos,
    }
    context.update(all_data)
    return render(request, 'creators_jobs.html', context)

@login_required
def creators_settings(request):
    all_data=brands_views.getting_all_data(request)
    userinfo = Userinfos.objects.get(user=request.user)
    user = request.user

    if request.method == 'POST' and request.POST.get("form_type") == "email":
        email = request.POST.get("email")
        phonenum = request.POST.get('phonenum')
        user.email = email
        user.save()
        userinfo.phonenum = phonenum
        userinfo.save()
        return redirect('creators_profile')
    
    if request.method == 'POST' and request.POST.get("form_type") == "password":
        new_password = request.POST.get("new_password")
        user.set_password(new_password)
        user.save()
        return redirect('creators_profile')
    
    
    context = {
        'userinfos':userinfo,
        'user':user,
    }
    context.update(all_data)
    return render(request, 'creators_settings.html',context)

@login_required
def creators_wallet(request):
    all_data=brands_views.getting_all_data(request)
    userinfo = Userinfos.objects.get(user=request.user)
    user = User.objects.get(username=all_data.get("current_username"))
    # available_earnings = sum(job.creators_price for job in brands_data.VideoOrderDetails.objects.filter(applied_creator=userinfo, order_status='completed'))
    completed_jobs = brands_data.VideoOrderDetails.objects.filter(applied_creator=userinfo, order_status='completed')
    pending_earnings = sum(job.creators_price for job in brands_data.VideoOrderDetails.objects.filter(applied_creator=userinfo).exclude(Q(order_status='completed') | Q(order_status='cancelled')))
    try:
        available_earnings = AvailableEarnings.objects.get(user=user)
    except AvailableEarnings.DoesNotExist:
        available_earnings = AvailableEarnings.objects.create(user=user)
    
    try:
        paymentinfo = PaymentInfo.objects.get(user=user)
    except PaymentInfo.DoesNotExist:
        paymentinfo = None

    if request.method == 'POST':
        withdrawal_amount = decimal(request.POST.get('withdrawal_amount'))
        if withdrawal_amount:
            if  withdrawal_amount <= available_earnings.available_earnings:
                available_earnings.available_earnings -= withdrawal_amount
                available_earnings.save()
                messages.success(request, f"Your ${withdrawal_amount} is on its way", extra_tags='withdrawal_success')
                subject = f"Creator requires a withdrawal"
                message = f""" The creator {userinfo.user.username} with PayPal account {paymentinfo.paypal_email} has requested a withdrawal of ${withdrawal_amount} """
                from_email = settings.EMAIL_HOST_USER
                to_email = "spotfayadmin@gmail.com"
                try:
                    send_mail(subject, message, from_email, [to_email])
                except:
                    print("Error sending email")

                return redirect(creators_wallet)

            # else:
            #     messages.error(request, "Insufficient balance")
            #     return redirect(creators_wallet)


    context = {
        'completed_jobs':completed_jobs,
        'available_earnings':available_earnings.available_earnings,
        'pending_earnings':pending_earnings,
        'userinfos':userinfo,
        'user':user,
        'paypal_account':paymentinfo
    }
    context.update(all_data)
    return render(request, 'creators_wallet.html',context)

@login_required
def creators_orderdetails(request, order_id):
    all_data=brands_views.getting_all_data(request)
    userinfos = Userinfos.objects.get(user=request.user)
    user = User.objects.get(username=all_data.get("current_username"))
    job_data = brands_data.VideoOrderDetails.objects.get(id=order_id)
    
    if request.method == 'POST':
        video_files = request.FILES.getlist('video_files')
        
        for file in video_files:
            print(file)
            video = brands_data.Video(video_file=file, user=userinfos, video_status=None)
            video.save()
            job = brands_views.VideoOrderDetails.objects.get(id=order_id)
            job.order_status = 'pending_approval'
            job.unable_to_disapprove_creator = True
            job.videos.add(video)
            job.save()
            print("videos saved succefully")
        return redirect('creators_orderdetails', order_id=order_id)


    context = {
        'job_data':job_data,
        'user':user,
        'userinfos':userinfos
    }
    context.update(all_data)
    return render(request, 'creators_orderdetails.html', context)

@login_required
def creators_paymentmethod(request):
    all_data=brands_views.getting_all_data(request)
    userinfos = Userinfos.objects.get(user=request.user)
    user = User.objects.get(username=all_data.get("current_username"))
    try:
        paymentinfo = PaymentInfo.objects.get(user=user)
    except PaymentInfo.DoesNotExist:
        paymentinfo = PaymentInfo.objects.create(user=user)


    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        paymentinfo.paypal_email = payment_method
        paymentinfo.save()
        return redirect("creators_wallet")


    context = {
        'paymentinfo':paymentinfo,
        'user':user,
        'userinfos':userinfos,
    }
    context.update(all_data)
    return render(request, 'creators_paymentmethod.html',context)

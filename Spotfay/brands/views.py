from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, get_user_model
from creators.models import PaymentInfo, CreatorsProfits, AvailableEarnings
from Authentications.models import Userinfos, CompanyData
from .models import VideoOrderDetails, Customer, PaymentMethod, ShipmentTrackingNum
from django.contrib import messages
import logging
from django.db.models import Q
# from creators.models import ....
from creators import views as creators_views
from Authentications import views as authentications_views
import inspect
from django.apps import apps
from django.db import models
from itertools import chain
from django.core.files.storage import FileSystemStorage
from django.core.files.temp import NamedTemporaryFile
from .services import get_or_create_stripe_customer
import stripe
from django.conf import settings
import os
from django.db.models import Prefetch
from .models import Video
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import Paginator


stripe.api_key = settings.STRIPE_SECRET_KEY

# Configure logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

userinfo = None
def getting_all_data(request):
    current_firstname = User.objects.get(id=request.user.id).first_name
    current_lastname = User.objects.get(id=request.user.id).last_name
    current_username = User.objects.get(id=request.user.id).username
    # current_usertype = getattr(Userinfos.objects.filter(user=request.user).first(), 'usertype', None)
    # current_country = Userinfos.objects.filter(username=current_username).first().country
    # current_city = Userinfos.objects.filter(username=current_username).first().city
    # current_address = Userinfos.objects.filter(username=current_username).first().address
    # current_postalcode = Userinfos.objects.filter(username=current_username).first().postalcode
    # current_phonenum = Userinfos.objects.filter(username=current_username).first().phonenum
    # current_birthdate = Userinfos.objects.filter(username=current_username).first().birthdate
    # current_userinfo = Userinfos.objects.filter(username=current_username).first().userinfo
    username = current_firstname + " " + current_lastname
    data = {
        'username':username.title(),
        'current_firstname':current_firstname,
        'current_lastname':current_lastname,
        'current_username':current_username,
        # 'current_usertype':current_usertype,
        # 'current_country':current_country,
        # 'current_city':current_city,
        # 'current_address':current_address,
        # 'current_postalcode':current_postalcode,
        # 'current_phonenum':current_phonenum,
        # 'current_birthdate':current_birthdate,
        # 'current_userinfo':current_userinfo,
    }
    return data

# Create your views here.
@login_required
def brands_dash(request):
    all_data=getting_all_data(request) 
    newuserinfo, _ = Userinfos.objects.get_or_create(user=request.user)
    try:
        newusercompany = CompanyData.objects.get(user=request.user)
    except CompanyData.DoesNotExist:
        newusercompany = CompanyData.objects.create(user=request.user)
        newusercompany.company_logo = "default_photos/spotfay_pro_com.png"
        newusercompany.save()
    
    user = request.user
    orders =  VideoOrderDetails.objects.filter(user=request.user)
    active_orders_applied_creators = VideoOrderDetails.objects.filter(user=request.user).exclude(order_status__in=['completed', 'cancelled', 'pending_creator_selecting'])
    active_orders = VideoOrderDetails.objects.filter(user=request.user).exclude(order_status__in=['completed', 'cancelled'])
    approve_content_orders = VideoOrderDetails.objects.filter(user=request.user, order_status__in=['pending_approval'])
    




    applied_creators = []

    requiring_delivery = active_orders.filter(Q(user=request.user)&(Q(order_status='pending_approval')|Q(order_status='processing'))&(Q(tracking_nums__tracking_num__isnull=True) | Q(tracking_nums__shipping_carrier__isnull=True)))

    for order in active_orders_applied_creators:
        if order.applied_creator: 
            applied_creators.append(order.applied_creator)


    context = {
        'no_of_orders':orders,
        'approve_content_order':approve_content_orders,
        'active_orders':active_orders,
        'applied_creators':applied_creators,
        'userinfos':newuserinfo,
        'user':user,
        'requiring_delivery':requiring_delivery,
    }
    context.update(all_data)
    return render(request, 'brands_dashboard.html',context)

@login_required
def brands_projectmanagment(request):
    all_data=getting_all_data(request)
    all_orders = VideoOrderDetails.objects.filter(user=request.user)
    active_orders = VideoOrderDetails.objects.filter(user=request.user, order_status__in=['pending_creator_approval', 'pending_creator_selecting'])    
    pending_approval = VideoOrderDetails.objects.filter(user=request.user, order_status='pending_approval')
    all_campaigns = []
    pending_approval_campaigns = []

    for order in all_orders:
        num_of_shipments = ShipmentTrackingNum.objects.filter(order=order).exclude(Q(tracking_num__isnull=True) | Q(shipping_carrier__isnull=True)).count()
        all_campaigns.append({
            'order':order,
            'num_of_shipments':num_of_shipments,
        })

    for order in pending_approval:
        num_of_shipments = ShipmentTrackingNum.objects.filter(order=order).exclude(Q(tracking_num__isnull=True) | Q(shipping_carrier__isnull=True)).count()
        pending_approval_campaigns.append({
            'order':order,
            'num_of_shipments':num_of_shipments,
        })
    

    context = {
        'all_campaigns':all_campaigns,
        'pending_approval_campaigns':pending_approval_campaigns,
        # 'active_orders':active_orders,
    }
    context.update(all_data)
    return render(request, 'brands_projects.html',context)

@login_required
def brands_shipping(request): 
    all_data=getting_all_data(request)
    orders = VideoOrderDetails.objects.filter(Q(user=request.user)&(Q(order_status='pending_approval')|Q(order_status='processing')))
                    
    if request.method == 'POST':
        tracking_num = request.POST.get('tracking_num')
        shipping_carrier = request.POST.get('shipping_carrier')
        order_id = request.POST.get('order_id')
        video_order = VideoOrderDetails.objects.get(id=order_id)
        try:
            existing_tracking_num = ShipmentTrackingNum.objects.get(order=video_order)
            existing_tracking_num.tracking_num = tracking_num
            existing_tracking_num.shipping_carrier = shipping_carrier
            existing_tracking_num.save()
        except ShipmentTrackingNum.DoesNotExist:
            ShipmentTrackingNum.objects.create(
                order=video_order,
                tracking_num=tracking_num,
                shipping_carrier=shipping_carrier
            )
        return redirect(brands_shipping)


    context = {
        'shipments':orders,
    }
    context.update(all_data)
    return render(request, 'brands_shipping.html',context)

@login_required
def brands_orderdetails(request, order_id):
    all_data=getting_all_data(request)
    order = VideoOrderDetails.objects.get(id=order_id)
    creators = order.selecting_creators.all()
    creator_userinfos =  Userinfos.objects.filter(user__in=[creator for creator in creators])
    order_content = order.videos.exclude(video_status='rejected')
    # print(order_content)
    
    origin_tracking_num = ''
    origin_shipping_carrier = ''

    # Step 3: Combine Userinfos data with User model data
    combined_creators = []
    for userinfo in creator_userinfos:
        # Get the corresponding User object
        user = userinfo.user
        previous_works = Video.objects.filter(user=userinfo, video_status='previous_works')
        
        # Append the Userinfos data along with the User's first name and last name
        combined_creators.append({
            'userinfo': userinfo,
            'user':user,
            'previous_works':previous_works,
        })
            
    try:
        origin_shipping_data, _ = ShipmentTrackingNum.objects.get_or_create(order=order)
        origin_tracking_num = origin_shipping_data.tracking_num
        origin_shipping_carrier = origin_shipping_data.shipping_carrier
    except ShipmentTrackingNum.DoesNotExist:
        origin_tracking_num = ''
        origin_shipping_carrier = ''

    if request.method == 'POST' and request.POST.get("form_type") == "delivery_info":
        tracking_num = request.POST.get("tracking_num")
        shipping_carrier = request.POST.get("shipping_carrier")
        subject = f"Update on {order.project_name} campaign"
        message = f"""The product shipment has been started \n its tracking number is {tracking_num} via {shipping_carrier}

Best regards,
Spotfay
{settings.SITE_LINK}
spotfaymarketing@gmail.com"""
        from_email = settings.EMAIL_HOST_USER
        to_email = user.email
        send_mail(subject, message, from_email, [to_email])

        try:
            existing_tracking_num = ShipmentTrackingNum.objects.get(order=order)
            existing_tracking_num.tracking_num = tracking_num
            existing_tracking_num.shipping_carrier = shipping_carrier
            existing_tracking_num.save()
        except ShipmentTrackingNum.DoesNotExist:
            ShipmentTrackingNum.objects.create(
                order=order,
                tracking_num=tracking_num,
                shipping_carrier=shipping_carrier
            )
        return redirect(brands_orderdetails, order_id=order_id)
        
    if request.method == 'POST' and request.POST.get("form_type") == "request_edit":
        video_id = request.POST.get("video_id")
        rejection_reason = request.POST.get("rejection_reason")
        creator = order.applied_creator
        creator_user = creator.user
        video = Video.objects.get(id=video_id)
        brand = order.user
        order.videos.remove(video)
        video.video_status = 'rejected'
        video.save()
        if order.videos.all():
            for video in order.videos.all():
                if video.video_status == None:
                    order.order_status = "pending_approval"
                    order.save()
                else:
                    order.order_status = "processing"
                    order.save()
        else:
            order.order_status = "processing"
            order.save()
                
        subject = f"Update on {order.project_name} project collaboration"
        message = f"""Dear {creator_user.first_name} {creator_user.last_name},

the video you have uploaded to the project {order.project_name} of the brand owner {brand.first_name} {brand.last_name}

Wich is {video.video_file.url} has been rejected by a request for some edits {rejection_reason}

Best regards,
Spotfay
{settings.SITE_LINK}
spotfaymarketing@gmail.com"""
        from_email = settings.EMAIL_HOST_USER
        to_email = creator_user.email
        send_mail(subject, message, from_email, [to_email])
        return redirect(brands_orderdetails, order_id=order_id)
     
    context = {
    'order':order,
    'creators':combined_creators,
    'order_content':order_content,
    'tracking_num':origin_tracking_num,
    'shipping_carrier':origin_shipping_carrier,
    }
    context.update(all_data)
    return render(request, 'brands_orderdetails.html',context)

@login_required
def brands_myprojects(request):
    all_data = getting_all_data(request)
    all_content = VideoOrderDetails.objects.filter(user=request.user)
    user = Userinfos.objects.get(user=request.user)
    all_videos = []

    for content in all_content:
        for video in content.videos.filter(video_status='approved'):
            all_videos.append(video)

    # Paginate the videos
    paginator = Paginator(all_videos, 5)  # Show 5 videos per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If it's an AJAX request, return JSON
        videos_data = []
        for video in page_obj:
            videos_data.append({
                'id': video.id,
                'video_url': video.video_file.url,
                'download_url': video.video_file.url,
                'download_name': video.video_file.name,
            })
        return JsonResponse({
            'videos': videos_data,
            'has_next': page_obj.has_next(),  # Indicates if there are more pages
        })

    context = {
        'all_videos': page_obj,
    }
    context.update(all_data)
    return render(request, 'brands_myprojects.html', context)

@login_required
def brands_companydata(request):
    all_data=getting_all_data(request)
    company_data, _ = CompanyData.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        userinfo, _ = Userinfos.objects.get_or_create(user=request.user)
        logo = request.FILES.get('logo')
        name = request.POST.get('name')
        activity = request.POST.get('activity')
        country = request.POST.get('country')
        weblink = request.POST.get('weblink')
        social = request.POST.get('social')
        if logo:
            company_data.company_logo = logo
            company_data.save()
        company_data.company_name = name
        company_data.company_activity = activity
        company_data.company_country = country
        company_data.company_weblink = weblink
        company_data.company_socialmedia_account = social
        company_data.save()
        userinfo.country = company_data.company_country
        userinfo.save()

    if company_data.company_name:
        company_shortname = "".join([word[0].upper() for word in company_data.company_name.split()])
    else:
        company_shortname = None


    context = {
        'company':company_data,
        'company_shortname':company_shortname,
    }
    context.update(all_data)
    return render(request, 'brands_companydata.html',context)

@login_required
def brands_ordervideo(request):
    all_data = getting_all_data(request)
    company_data = CompanyData.objects.get(user=request.user)

    if not all(field != '' and field is not None for key, field in company_data.__dict__.items() if key != 'company_socialmedia_account'):
        messages.error(request, "Add your brand first")
        return redirect('brands_dash')

    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        product_link = request.POST.get('product_link')
        product_img = request.FILES.get('product_img')
        video_duration = request.POST.get('video_duration')
        video_size = request.POST.get('video_size')
        video_type = request.POST.get('video_type')
        no_of_videos = request.POST.get('no_of_videos')
        additional_notes = request.POST.get('additional_notes')
        total_price = request.POST.get('totalprice')
        video_price = request.POST.get('videoprice')
        
        # Save the uploaded file to a permanent location
        fs = FileSystemStorage()
        filename = fs.save(product_img.name, product_img)
        product_img_url = os.path.join(settings.MEDIA_URL, filename)
        
        try:
          last_video_order = VideoOrderDetails.objects.filter(user=request.user).latest('id')
        except VideoOrderDetails.DoesNotExist:
            # handle the case where no object is found
            pass
        review_context = {
            'project_name':project_name,
            'product_name':product_name,
            'product_description':product_description,
            'product_link':product_link,
            'product_img':product_img_url,
            'video_duration':video_duration,
            'video_size':video_size,
            'video_type':video_type,
            'no_of_videos':no_of_videos,
            'additional_notes':additional_notes,
            'total_price':total_price,
            'video_price':video_price,
        }
        request.session['product'] = review_context
        request.session['project_name'] = project_name
        request.session['product_name'] = product_name
        request.session['product_description'] = product_description
        request.session['product_link'] = product_link
        request.session['product_img'] = product_img_url
        request.session['video_duration'] = video_duration
        request.session['video_size'] = video_size
        request.session['video_type'] = video_type
        request.session['no_of_videos'] = no_of_videos
        request.session['additional_notes'] = additional_notes
        request.session['total_price'] = total_price
        request.session['video_price'] = video_price
        review_context.update(all_data)
        return render(request, "brands_orderreview.html", review_context)



    # Check the other tables as usual
    # combined_query_set = [
    #     CompanyData.objects.get(user=request.user),
    #     User.objects.get(user=request.user),
    # ]
    # for obj in combined_query_set:
    #     if all(value is not None and value!= '' and value != "None" for value in obj.__dict__.values()):
    #         pass
    #     else:
    #         messages.error(request, "Please, fill out the required data fields to be able to order a video!")
    #         return redirect('brands_dash')

    context = {

    }
    context.update(all_data)
    return render(request, 'brands_ordervideo.html',context)

@login_required
def brands_paymentreview(request):
    all_data=getting_all_data(request)
    stripe_customer_id = get_or_create_stripe_customer(request.user)
    customer = Customer.objects.get(stripe_customer_id=stripe_customer_id)
    payment_methods = PaymentMethod.objects.filter(customer=customer)
    video_size = request.session['product'].get('video_size')
    platform_fee = round(int(request.session.get('total_price')) * 0.15)
    total_fee_price = int(request.session.get('total_price')) + platform_fee
    request.session['total_fee_price'] = total_fee_price
    if video_size == '9:16':
        video_size = 'شاشة كاملة 9:16'
    elif video_size == '16:9':
        video_size = 'شاشة مستطيلة 16:9'
    elif video_size == '1:1':
        video_size = 'شاشة مربعة 1:1'
        
    product_img_url = request.session.get('product_img')
    
    review_context = {
    'project_name': request.session.get('project_name'),
    'product_name': request.session.get('product_name'),
    'product_description': request.session.get('product_description'),
    'product_link': request.session.get('product_link'),
    'video_duration': request.session.get('video_duration'),
    'video_size': video_size,
    'video_type': request.session.get('video_type'),
    'no_of_videos': request.session.get('no_of_videos'),
    'additional_notes': request.session.get('additional_notes'),
    'total_price': request.session.get('total_price'),
    'video_price': request.session.get('video_price'),
    }

    context = {
        'payment_methods':payment_methods,
        'total_fee_price':total_fee_price,
        'platform_fee':platform_fee,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    context.update(all_data)
    context.update(review_context)
    return render(request, 'brands_paymentrev.html',context)

@login_required
def payment_method_delete(request, payment_id, reversing_view):
    stripe_customer_id = get_or_create_stripe_customer(request.user)
    customer = Customer.objects.get(stripe_customer_id=stripe_customer_id)
    # payment_methods = PaymentMethod.objects.filter(customer=customer)
    payment_method = PaymentMethod.objects.get(id=payment_id)
    print(payment_method)
    payment_method.delete()
    return redirect(reversing_view)

@login_required
def brands_account(request):
    all_data = getting_all_data(request)
    newuserinfo, _ = Userinfos.objects.get_or_create(user=request.user)
    stripe_customer_id = get_or_create_stripe_customer(request.user)
    customer = Customer.objects.get(stripe_customer_id=stripe_customer_id)
    payment_methods = PaymentMethod.objects.filter(customer=customer)

    if request.method == 'POST' and request.POST.get("form_type") == "profile_information":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        country = request.POST.get("country")
        phonenum = request.POST.get("phonenum")
        newuserinfo.country = country
        newuserinfo.phonenum = phonenum
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()
        newuserinfo.save()
        return redirect("brands_account")

    if request.method == 'POST' and request.POST.get("form_type") == "email":
        email = request.POST.get("email")
        request.user.email = email
        request.user.save()
        return redirect("brands_account")

    # adding_card
    if request.method == 'POST' and request.POST.get("form_type") == "add_card":
        print("hello new card welcom to the real world")
        card_holder_name = request.POST.get("card_holder_name")
        stripe_token = request.POST.get('stripeToken')
        try:
            payment_method = stripe.PaymentMethod.create(
                type="card",
                card={"token": stripe_token},
            )
            stripe.PaymentMethod.attach(
                payment_method.id,
                customer=stripe_customer_id,
            )
            # Save the new payment method in the local database
            payment_method_data = payment_method.card
            PaymentMethod.objects.create(
                customer=customer,
                card_holder_name=card_holder_name.upper(),
                stripe_payment_method_id=payment_method.id,
                card_type=payment_method_data.brand.capitalize(),
                last4=payment_method_data.last4,
                exp_month=payment_method_data.exp_month,
                exp_year=payment_method_data.exp_year,
                default=payment_methods.count() == 0  # Set as default if it's the first method
            )
            return redirect('brands_account')
        except stripe.error.CardError as e:
            messages.error(request, "Card error: {}".format(e))
            return redirect('brands_account')
        except stripe.error.StripeError as e:
            messages.error(request, "Stripe error: {}".format(e))
            return redirect('brands_account')
        except Exception as e:
            messages.error(request, "An unexpected error occurred. Please try again.")
            return redirect('brands_account')

    context = {
        'userinfos': newuserinfo,
        'user': request.user,
        'payment_methods': payment_methods,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'orders':VideoOrderDetails.objects.filter(user=request.user),
    }
    context.update(all_data)
    return render(request, 'brands_account.html', context)
  
@login_required
def brands_paymentgateway(request): 
    all_data = getting_all_data(request)
    company_data = CompanyData.objects.get(user=request.user)
    print(company_data)
    if request.method == 'POST':
        use_saved_method = request.POST.get('use_saved_method') == 'true'
        total_price = request.session['total_price']
        customer = Customer.objects.get(user=request.user)
        stripe_customer_id = customer.stripe_customer_id
        image_url = request.session.get('product_img')
        total_fee_price = request.session.get('total_fee_price')

        # Debug logging
        logger.debug(f"Total price from session: {total_fee_price}")

        try:
            total_price_cents = int(total_fee_price) * 100  # Convert to cents
            logger.debug(f"Total price in cents: {total_price_cents}")
        except ValueError as e:
            logger.error(f"Invalid total price: {total_fee_price}, error: {e}")
            return redirect('payment_failed')

        if use_saved_method:
            payment_method_id = request.POST.get('payment_method_id')
            try:
                intent = stripe.PaymentIntent.create(
                    amount=total_price_cents,
                    currency='usd',
                    customer=stripe_customer_id,
                    payment_method=payment_method_id,
                    off_session=True,
                    confirm=True,
                )
                logger.debug(f"Payment intent created: {intent.id}")

                # Save the order details
                payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
                VideoOrderDetails.objects.create(
                    user=request.user,
                    project_name=request.session['project_name'],
                    product_name=request.session['product_name'],
                    product_description=request.session['product_description'],
                    product_link=request.session['product_link'],
                    product_img=image_url,
                    video_duration=request.session['video_duration'],
                    video_size=request.session['video_size'],
                    video_type=request.session['video_type'],
                    num_of_videos=request.session['no_of_videos'],
                    additional_notes=request.session['additional_notes'],
                    video_price=request.session['video_price'],
                    email=request.user.email,
                    total_price=total_fee_price,
                    creators_price=total_price,
                    brand_name=company_data.company_name,
                    stripe_charge_id=intent.id,
                    last4=payment_method.card.last4,
                    card_type=payment_method.card.brand,
                    company=company_data,
                )
                messages.success(request, "Order Placed Successfully!")
                return redirect('brands_dash')
            except stripe.error.CardError as e:
                logger.error(f"Card error: {e}")
                return redirect('payment_failed')
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error: {e}")
                return redirect('payment_failed')
        else:
            stripe_token = request.POST.get('stripeToken')
            card_holder_name = request.POST.get('card_holder_name')
            try:
                payment_method = stripe.PaymentMethod.create(
                    type="card",
                    card={"token": stripe_token},
                )
                logger.debug(f"Payment method created: {payment_method.id}")
                stripe.PaymentMethod.attach(payment_method.id, customer=stripe_customer_id)
                logger.debug(f"Payment method attached to customer: {stripe_customer_id}")

                # Save the payment method in the local database
                PaymentMethod.objects.create(
                    customer=customer,
                    card_holder_name=card_holder_name.upper(),
                    stripe_payment_method_id=payment_method.id,
                    card_type=payment_method.card.brand,
                    last4=payment_method.card.last4,
                    exp_month=payment_method.card.exp_month,
                    exp_year=payment_method.card.exp_year,
                )

                intent = stripe.PaymentIntent.create(
                    amount=total_price_cents,
                    currency='usd',
                    customer=stripe_customer_id,
                    payment_method=payment_method.id,
                    off_session=True,
                    confirm=True,
                )
                logger.debug(f"Payment intent created: {intent.id}")

                # Save the order details
                VideoOrderDetails.objects.create(
                    user=request.user,
                    project_name=request.session['project_name'],
                    product_name=request.session['product_name'],
                    product_description=request.session['product_description'],
                    product_link=request.session['product_link'],
                    product_img=image_url,
                    video_duration=request.session['video_duration'],
                    video_size=request.session['video_size'],
                    video_type=request.session['video_type'],
                    num_of_videos=request.session['no_of_videos'],
                    additional_notes=request.session['additional_notes'],
                    video_price=request.session['video_price'],
                    email=request.user.email,
                    total_price=total_fee_price,
                    creators_price=total_price,
                    brand_name=company_data.company_name,
                    stripe_charge_id=intent.id,
                    last4=payment_method.card.last4,
                    card_type=payment_method.card.brand,
                    company=company_data,
                )


                messages.success(request, "Order Placed Successfully!")
                return redirect('brands_dash')
            except stripe.error.CardError as e:
                logger.error(f"Card error: {e}")
                messages.error(request, "Card error: your card has been declined".format(e))
                return redirect('brands_paymentreview')
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error: {e}")
                messages.error(request, "Stripe error: {}".format(e))
                return redirect('brands_paymentreview')
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                messages.error(request, "An unexpected error occurred. Please try again.")
                return redirect('brands_paymentreview')
            
@login_required
def brands_approvingcreator(request, order_id, creator_userinfos_id):
    creator = Userinfos.objects.get(id=creator_userinfos_id)
    order = VideoOrderDetails.objects.get(id=order_id)
    creator_user = creator.user
    brand = order.user
    
    order.order_status = 'processing'
    order.applied_creator = creator
    order.save()
    subject = f"CONGRATULATIONS🎉 on Your selection by {brand.first_name} {brand.last_name} of the {order.project_name} project!"
    message = f"""Dear {creator_user.first_name} {creator_user.last_name},

I hope you’re doing great! I’m thrilled to share some exciting news—{brand.first_name} {brand.last_name} has chosen you to collaborate with {order.brand_name}. Out of many talented creators, your work truly shone, and this selection speaks volumes about your creativity and dedication.

This is a fantastic achievement and a significant milestone in your journey. We’re all eager to see the incredible work you’ll bring to this project.

Please check your email for further updates and next steps regarding this collaboration. 

Congratulations on this achievement! It's a well-deserved milestone in your career, and we’re confident that this partnership will only add to your continued success.

Looking forward to seeing your creative magic in action!

Best regards,
Spotfay
{settings.SITE_LINK}
spotfaymarketing@gmail.com"""
    from_email = settings.EMAIL_HOST_USER
    to_email = creator_user.email
    send_mail(subject, message, from_email, [to_email])
    return redirect('brands_orderdetails', order_id=order_id)

# cancel creator approval
@login_required
def brands_disapprovingcreator(request, order_id, creator_userinfos_id):
    order = VideoOrderDetails.objects.get(id=order_id)
    creator_userinfos = order.applied_creator
    creator_user = creator_userinfos.user
    brand = User.objects.get(username=order.user.username)
    
    try:
        product_shipment = ShipmentTrackingNum.objects.get(order=order)
        product_shipment.delete()
    except ShipmentTrackingNum.DoesNotExist:
        pass

    order.order_status = 'pending_creator_approval'
    order.applied_creator = None  # Set applied_creator to None
    order.save()
    
    subject = f"Update on {order.project_name} project collaboration"
    message = f"""Dear {creator_user.first_name} {creator_user.last_name},

We are sorry to inform you that {brand.first_name} {brand.last_name} has cancelled their approval for the {order.project_name} project. We understand that this news may be disappointing, and we want to assure you that this decision is in no way a reflection of your talent or abilities.

Please know that we appreciate your interest in collaborating with {order.brand_name} and value the time you invested in this opportunity. We encourage you to continue seeking out new projects and collaborations that align with your goals and passions.

If you have any questions or concerns, please don't hesitate to reach out to us. We're always here to support you.

Best regards,
Spotfay
{settings.SITE_LINK}
spotfaymarketing@gmail.com"""
    from_email = settings.EMAIL_HOST_USER
    to_email = creator_user.email
    send_mail(subject, message, from_email, [to_email])
    return redirect('brands_orderdetails', order_id=order_id)

# video approval
@login_required
def brands_videoapproval(request, order_id, video_id):
    # creator = Userinfos.objects.get(id=creator_userinfos_id)
    order = VideoOrderDetails.objects.get(id=order_id)
    creator_userinfo = order.applied_creator
    creator_user = creator_userinfo.user

    try:
        available_earnings = AvailableEarnings.objects.get(user=creator_user)
    except AvailableEarnings.DoesNotExist:
        available_earnings = AvailableEarnings.objects.create(user=creator_user)

    try:
        paypal = PaymentInfo.objects.get(user=creator_user).paypal_email
    except PaymentInfo.DoesNotExist:
        paypal = None

    video = Video.objects.get(id=video_id)
    video.video_status = 'approved'
    video.save()
    order_videos = order.videos.filter(video_status="approved")
    if len(order_videos) == int(order.num_of_videos):
        available_earnings.available_earnings = available_earnings.available_earnings + order.creators_price
        CreatorsProfits.objects.create(
            creator=creator_user,
            order=order,
            amount=order.creators_price,
            paypal=paypal,
        )
        order.order_status = 'completed'
        order.save()
        available_earnings.save()
        print(available_earnings.available_earnings)
        
        subject = f"Order {order.project_name} by ID {order.id} has been completed by the creator!"
        message = f"""Dear Admin,

The order {order.project_name} has been completed by the creator {order.applied_creator.user.username}, So that he has a profit wich is ${order.creators_price}. Here are the order details:

Project Name: {order.project_name}
Product Name: {order.product_name}
Product Link: {order.product_link}
Video Duration: {order.video_duration}
Video Size: {order.video_size}
Video Type: {order.video_type}
Number of Videos: {order.num_of_videos}
Video Price: ${order.video_price}
Total Price: ${order.total_price}
Creators Price: ${order.creators_price}
Brand Name: {order.brand_name}
Stripe Charge ID: {order.stripe_charge_id}
Last 4 Digits of Card: {order.last4}
Card Type: {order.card_type}
Company: {order.company}

Best regards,
Spotfay
{settings.SITE_LINK}
spotfaymarketing@gmail.com"""
        from_email = settings.EMAIL_HOST_USER
        to_email = "spotfayadmin@gmail.com"
        send_mail(subject, message, from_email, [to_email])
        
    else:
       for video in order.videos.all():
            if video.video_status == None:
                order.order_status = "pending_approval"
                order.save()
            else:
                order.order_status = "processing"
                order.save()
    
    # send and email here to notify the creator that the video has been approved
     
    return redirect('brands_orderdetails', order_id=order_id)
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, get_user_model, logout
from urllib.parse import urlparse, parse_qs
from .models import Userinfos, CompanyData
from django.urls import reverse
import secrets
# from creators.models import .....
# from brands.models import .....
from creators import views as creators_views
from brands import views as brands_views
from social_core.exceptions import AuthCanceled
from social_core import exceptions

# Create your views here.

session_usertype = ""
current_user = get_user_model()

def get_next_url(request):
    next_url = request.GET.get('next')
    if next_url:
        request.session['NextUrl']=next_url
        return next_url
        
    return None

def brandslogin_view(request):
    # creating session variable that carry the user type which is 'brand owner'
    global session_usertype
    session_usertype = "brand owner"
    request.session['session_usertype']=session_usertype
    next_url = get_next_url(request)
    request.session['NextUrl']=next_url
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('brands_dash')  # Redirect to the brands dashboard if already logged in

    if request.method == 'POST':
        email_or_username = request.POST['email']
        password = request.POST['pass']
        try:
            # username creation
            if "@" in email_or_username:
                parts = email_or_username.split("@")
                username = parts[0]
                user = authenticate(request, username=username, password=password)
            else:
                user = authenticate(request, username=email_or_username, password=password)
            if user:
                login(request, user)
                if next_url:
                    return redirect(next_url)
                return redirect('brands_dash')
            else:
                return render(request, 'login.html', {'error_message': "Invalid email/username or password"})
        except Exception as e:
            return redirect('brandslogin_view')
    else:
        return render(request, 'login.html')

def creatorslogin_view(request):
    # creating session variable that carry the user type which is 'content creator'
    global session_usertype
    session_usertype = "content creator"
    request.session['session_usertype']=session_usertype
    next_url = request.session.get('NextUrl')
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('creators_dash')  # Redirect to the creators dashboard if already logged in

    if request.method == 'POST':
        email_or_username = request.POST['email']
        password = request.POST['pass']
        # username creation
        if "@" in email_or_username:
            parts = email_or_username.split("@")
            username = parts[0]
            user = authenticate(request, username=username, password=password)
        else:
            user = authenticate(request, username=email_or_username, password=password)
        if user is not None:
            login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect('creators_dash')
        else:
            return render(request, 'creators_login.html', {'error_message': "Invalid email or password"})
    else:
        return render(request, 'creators_login.html')

def create_new_user(username, email, password, first_name, last_name):
    # Check if the email address is already in use
    if User.objects.filter(email__iexact=email).exists():
        return False, "Email address is already in use"

    # Create a new user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    
    return True, "User created successfully"

def brands_signup(request):
    # creating session variable that carry the user type which is 'brand owner'
    global session_usertype
    session_usertype = "brand owner"
    request.session['session_usertype']=session_usertype
    next_url = request.session.get('NextUrl')
    if request.method == 'POST':
        email = request.POST['email']
        # username creation
        if "@" in email:
            parts = email.split("@")
            usernamed = parts[0]
        username = usernamed
        password = request.POST['pass2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        request.session['username']='ahmed mido'

        success, message = create_new_user(username, email, password, first_name, last_name)
        if success:
            # User created successfully, redirect to a success page
            user = authenticate(request, username=username, password=password)
            login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect('creators_dash')
        else:
            # Display an error message
            return render(request, 'signup.html', {'error_message': message})
    else:
        context = {
            'next_url':next_url,
        }
        return render(request, 'signup.html', context)

def creators_signup(request):
    # creating session variable that carry the user type which is 'content creator'
    global session_usertype
    session_usertype = "content creator"
    request.session['session_usertype']=session_usertype
    next_url = request.session.get('NextUrl')
    if request.method == 'POST':
        email = request.POST['email']
        # username creation
        if "@" in email:
            parts = email.split("@")
            usernamed = parts[0]
        username = usernamed
        password = request.POST['pass2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        request.session['username']='ahmed mido'

        success, message = create_new_user(username, email, password, first_name, last_name)
        if success:
            # User created successfully, redirect to a success page
            user = authenticate(request, username=username, password=password)
            login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect('creators_dash')
        else:
            # Display an error message
            return render(request, 'creators_signup.html', {'error_message': message})
    else:
        return render(request, 'creators_signup.html')

def privacy_policy(request):
    return render(request, 'privacypolicy.html')

def creators_logout(request):
    logout(request)
    return redirect('creators_login')

def brands_logout(request):
    logout(request)
    return redirect('brands_login')
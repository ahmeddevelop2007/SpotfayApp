"""
URL configuration for Spotfay project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from Authentications import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('creators/', include('creators.urls')),
    path('brands/', include('brands.urls')),
    # path('Login/redirector/', views.redirector, name='redirector'),
    path('creators/Login/', views.creatorslogin_view, name='creators_login'),
    path('brands/Login/', views.brandslogin_view, name='brands_login'),
    path("creators/signup/", views.creators_signup, name='creators_signup'),
    path("brands/signup/", views.brands_signup, name='brands_signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('creators/logout/', views.creators_logout, name='creators_logout'),
    path('brands/logout/', views.brands_logout, name='brands_logout'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path("service_and_privacy_policy/", views.privacy_policy, name='privacy_policy'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

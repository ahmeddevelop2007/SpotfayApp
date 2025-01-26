# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.creators_offers, name='creators_dash'),
    path('offers/', views.creators_offers, name='creators_offers'),
    path('load_more_jobs/', views.load_more_jobs, name='load_more_jobs'),
    path('profile/', views.creators_profile, name='creators_profile'),
    path('delete_video/<int:video_id>/', views.creators_deletevideo, name='creators_deletevideo'),
    path('jobs/', views.creators_jobs, name='creators_jobs'),
    path('profile/login_info/', views.creators_settings, name='creators_settings'),
    path('wallet/', views.creators_wallet, name='creators_wallet'),
    path('wallet/payment_method/', views.creators_paymentmethod, name='payment_method'),
    path('jobs/order_<int:order_id>/', views.creators_orderdetails, name='creators_orderdetails'),
    path('jobs/order_<int:order_id>/delete_video_<int:video_id>/', views.delete_video, name='delete_video'),
]

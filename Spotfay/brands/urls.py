# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.brands_dash, name='brands_dash'),
    path('dashboard/', views.brands_dash, name='brands_dash'),
    path('account/', views.brands_account, name='brands_account'),
    path('campaigns/', views.brands_projectmanagment, name='brands_projectmanagment'),
    path('shipments/', views.brands_shipping, name='brands_shipping'),
    path('myprojects/', views.brands_myprojects, name='brands_myprojects'),
    path('companydata/', views.brands_companydata, name='brands_companydata'),
    path('campaigns/new/', views.brands_ordervideo, name='brands_ordervideo'), 
    path('campaigns/new/payment/', views.brands_paymentreview, name='brands_paymentreview'),
    path('campaigns/new/payment/<int:payment_id>/<str:reversing_view>/', views.payment_method_delete, name='payment_method_delete'),
    path('paymentgateway/', views.brands_paymentgateway, name='brands_paymentgateway'),
    path('campaigns/<int:order_id>/', views.brands_orderdetails, name='brands_orderdetails'),
    path('campaign/<int:order_id>/approving_creator/<int:creator_userinfos_id>/', views.brands_approvingcreator, name='brands_approvingcreator'),
    path('campaign/<int:order_id>/disapproving_creator/<int:creator_userinfos_id>/', views.brands_disapprovingcreator, name='brands_disapprovingcreator'),
    path('campaign/<int:order_id>/video_approval/<int:video_id>/', views.brands_videoapproval, name='brands_videoapproval'),
]

from django.db import models
from django.templatetags.static import static
from datetime import datetime, date
from django.contrib.auth.models import User

# Create your models here.

# table (userifos) to store every user data
class Userinfos(models.Model):
    usertypes = [
        ('content creator','Content Creator'),
        ('brand owner','Brand Owner')
    ]
    gender = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userinfos', null=True)
    user_profile = models.ImageField(upload_to='photos/users_profile_images/%y/%m/%d', default='default_photos/spotfay_pro_com.png')
    country = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=100, null=True)
    postalcode = models.IntegerField(null=True)
    phonenum = models.IntegerField(null=True)
    birthdate = models.DateField(max_length=100, null=True)
    gender = models.CharField(max_length=100, choices=gender, null=True)
    userinfo = models.CharField(max_length=20000, null=True)
    insta_account = models.CharField(max_length=2000, null=True)
    tiktok_account = models.CharField(max_length=2000, null=True)
    telegram_account = models.CharField(max_length=2000, null=True)
    usertype = models.CharField(max_length=50, choices=usertypes, default='brand owner')
    def  __str__(self):
        return f'infos of user {self.user.username}'


class CompanyData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='companydata', null=True)
    company_name = models.CharField(max_length=150, null=True)
    company_activity = models.CharField(max_length=150, null=True)
    company_country = models.CharField(max_length=150, null=True)
    company_logo = models.ImageField(upload_to='photos/companylogo/%y/%m/%d', default='default_photos/spotfay_pro_com.png')
    company_weblink = models.CharField(max_length=150, null=True)
    company_socialmedia_account = models.CharField(max_length=150, null=True)
    def __str__ (self):
        return f'{self.company_name} for {self.user.username}'
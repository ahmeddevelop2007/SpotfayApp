from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from Authentications import models as authentications_data

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return f"{self.user.username}"

class PaymentMethod(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payment_methods')
    card_holder_name = models.CharField(max_length=255, null=True)
    stripe_payment_method_id = models.CharField(max_length=255)
    card_type = models.CharField(max_length=255)
    last4 = models.CharField(max_length=4)
    exp_month = models.IntegerField(null=True)
    exp_year = models.IntegerField(null=True)
    default = models.BooleanField(default=False)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.card_holder_name}'s Card"

class Video(models.Model):
    status = [
        ('approved','approved'),
        ('rejected','rejected'),
        ('previous_works','previous_works'),
    ]
    video_file = models.FileField(upload_to='videos/%y/%m/%d')
    video_status = models.CharField(max_length=50, choices=status, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(authentications_data.Userinfos, on_delete=models.CASCADE, related_name='videos')

    def __str__(self):
        return f'{self.video_status} by {self.user.user.username}'

class VideoOrderDetails(models.Model):
    status = [
        ('pending_creator_selecting','pending_creator_selecting'),
        ('pending_approval','pending_approval'),
        ('pending_creator_approval','pending_creator_approval'),
        ('completed','completed'),
        ('processing','processing'),
        ('cancelled','cancelled')
    ]
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE, null=True)
    selecting_creators = models.ManyToManyField(User, related_name='creators')
    applied_creator = models.ForeignKey(authentications_data.Userinfos, on_delete=models.CASCADE, related_name='orders', null=True)
    unable_to_disapprove_creator = models.BooleanField(default=False)
    videos = models.ManyToManyField(Video, related_name='orders')
    project_name = models.CharField(max_length=60, null=True)
    product_name = models.CharField(max_length=60, null=True)
    product_description = models.CharField(max_length=500, null=True)
    product_link = models.CharField(max_length=60, null=True)
    product_img = models.ImageField(upload_to='photos/orders/product_img/%y/%m/%d', null=True)
    video_duration = models.IntegerField(null=True)
    video_size = models.CharField(max_length=60, null=True)
    video_type = models.CharField(max_length=60, null=True)
    num_of_videos = models.IntegerField(null=True)
    additional_notes =models.CharField(max_length=2000, null=True)
    video_price = models.IntegerField(null=True)
    brand_name = models.CharField(max_length=60, null=True)
    # order stripe details
    email = models.EmailField(null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    creators_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    stripe_charge_id = models.CharField(max_length=100, null=True)
    last4 = models.CharField(max_length=4, null=True)
    card_type = models.CharField(max_length=50, null=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    order_status = models.CharField(max_length=50, choices=status, default='pending_creator_selecting')
    company = models.ForeignKey(authentications_data.CompanyData, on_delete=models.DO_NOTHING, related_name='comapny_orders', null=True)
    # shipment_tracking_num = models.ForeignKey(ShipmentTrackingNum, on_delete=models.CASCADE, related_name='tracking_nums', null=True)
    
    def __str__(self):
        return f'Transaction for {self.product_name} by {self.user.username}'

class ShipmentTrackingNum(models.Model):
    order = models.ForeignKey(VideoOrderDetails, on_delete=models.CASCADE, related_name='tracking_nums', null=True)
    tracking_num = models.CharField(max_length=200, null=True)
    shipping_carrier = models.CharField(max_length=100, null=True)

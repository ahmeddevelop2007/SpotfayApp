from django.contrib import admin
from .models import VideoOrderDetails, Customer, PaymentMethod, Video, ShipmentTrackingNum


class VideoOrderDetailsAdmin(admin.ModelAdmin):
    list_display =  ['project_name', 'user', 'unable_to_disapprove_creator', 'company', 'order_status']
    list_filter = ['order_status', 'created_at', 'unable_to_disapprove_creator']
    search_fields = ['user__username', 'project_name', 'product_name', 'video_size', 'video_type', 'video_price', 'brand_name', 'email', 'total_price', 'creators_price', 'stripe_charge_id', 'last4', 'card_type', 'bank_name', 'created_at']

class VideosAdmin(admin.ModelAdmin):
    list_display = ['video_status', 'uploaded_at', '__str__']
    list_filter = ['video_status', 'uploaded_at']
    search_fields = ['video_status', 'video_file', 'uploaded_at']

# Register your models here.
admin.site.register(VideoOrderDetails, VideoOrderDetailsAdmin)
admin.site.register(Customer)
admin.site.register(PaymentMethod)
admin.site.register(Video, VideosAdmin)
admin.site.register(ShipmentTrackingNum)
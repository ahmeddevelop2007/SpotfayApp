from django.contrib import admin
from .models import PaymentInfo, CreatorsProfits, AvailableEarnings
# Register your models here.


class AvailableEarningsAdmin(admin.ModelAdmin):
    list_display = ['user', 'id', 'available_earnings']

class CreatorsProfitsAdmin(admin.ModelAdmin):
    list_display = ['creator', 'order', 'amount', 'paid']
    list_filter = ['paid']
    search_fields = ['creator__username', 'amount', 'paypal']

admin.site.register(PaymentInfo)
admin.site.register(CreatorsProfits, CreatorsProfitsAdmin)
admin.site.register(AvailableEarnings, AvailableEarningsAdmin)
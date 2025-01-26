from django.contrib import admin
from .models import Userinfos, CompanyData

# Register your models here.
class UserinfosAdmin(admin.ModelAdmin):
    list_display = ['user','country','city','postalcode','birthdate']
    search_fields = ['user', 'country','city','postalcode','birthdate']
    list_filter = ['country','city','postalcode']

class CompanyDataAdmin(admin.ModelAdmin):
    list_display = ['user','company_name','company_activity','company_country']
    search_fields = ['user', 'company_name','company_activity','company_country']
    list_filter = ['company_country']

admin.site.site_header = 'Spotfay Administration'
admin.site.site_title = 'Spotfay site admin'
admin.site.register(Userinfos, UserinfosAdmin)
admin.site.register(CompanyData, CompanyDataAdmin)
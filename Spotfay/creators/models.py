from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from Authentications import models as authentications_data
from brands import models as brands_data

class AvailableEarnings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    available_earnings = models.DecimalField(max_digits=100, decimal_places=2, null=True, default=0)

# Create your models here.
class PaymentInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    paypal_email = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Paypal email"
    
class CreatorsProfits(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    order = models.OneToOneField(brands_data.VideoOrderDetails, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2, null=True)
    paypal = models.EmailField(max_length=50, null=True)
    paid = models.BooleanField(default=False)
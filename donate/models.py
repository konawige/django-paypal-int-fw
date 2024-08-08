from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.
class DonateClient(models.Model):
    name = models.CharField(max_length=56)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_payment = models.DateField(auto_now_add=True)
    status = models.TextField(blank=True, default='N/A')
    invoice_id = models.CharField(max_length=128, blank=True, default='')

    def clean(self):
        if self.amount<= 0:
            raise ValidationError({"amount": "Amount must be positive"})

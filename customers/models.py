from django.core.urlresolvers import reverse
from django.db import models

class Customer(models.Model):
    name = models.CharField('Navn', max_length=200)
    is_active = models.BooleanField('Aktiv', default=True)
    
    # Stats
    sms_sent = models.IntegerField('SMS\'er afsendt', default=0)
    credit = models.FloatField('Kredit', default=0.0)

    # Prices
    subscription_price = models.FloatField('Abonnementspris', default=100.0)
    sms_price = models.FloatField('SMS-pris', default=1.0)

    def get_absolute_url(self):
        return reverse('customer_detail', args=[self.pk])

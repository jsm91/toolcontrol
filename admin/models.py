from django.db import models

class Customer(models.Model):
    name = models.CharField('Navn', max_length=200)
    
    # Stats
    sms_sent = models.IntegerField('SMS\'er afsendt', default=0)

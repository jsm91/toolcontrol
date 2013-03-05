# -*- coding:utf-8 -*-
import datetime

from django.core.urlresolvers import reverse
from django.db import models
from paypal.standard.ipn.signals import payment_was_successful

class Customer(models.Model):
    # Info
    name = models.CharField('Navn', max_length=200)
    is_active = models.BooleanField('Aktiv', default=True)
    address = models.CharField('Adresse', max_length=200)
    zip_code = models.IntegerField('Postnummer')
    town = models.CharField('By', max_length=200)
    
    # Stats
    sms_sent = models.IntegerField('SMS\'er afsendt', default=0)
    credit = models.FloatField('Kredit', default=0.0)

    # Prices
    subscription_price = models.FloatField('Abonnementspris', default=100.0)
    sms_price = models.FloatField('SMS-pris', default=1.0)

    def get_absolute_url(self):
        return reverse('customer_detail', args=[self.pk])

    def __unicode__(self):
        return self.name

    def events(self):
        from tools.models import Event
        return Event.objects.filter(tool__model__category__customer=self, 
                                    start_date__gte=datetime.datetime.now()-datetime.timedelta(days=30)).count()

    def logins(self):
        from tools.models import Login
        return Login.objects.filter(employee__customer=self,
                                    timestamp__gte=datetime.datetime.now()-datetime.timedelta(days=30)).count()

    def tickets(self):
        from tools.models import Ticket
        return Ticket.objects.filter(reported_by=self).count()

    def transactions(self):
        return Transaction.objects.filter(customer=self).order_by('-timestamp')

class Transaction(models.Model):
    customer = models.ForeignKey(Customer)
    credit = models.FloatField('Beløb')
    description = models.TextField()
    is_confirmed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

def confirm_transaction(sender, **kwargs):
    transaction_id = int(sender.invoice)
    transaction = Transaction.objects.get(id=transaction_id)
    transaction.is_confirmed = True
    transaction.save()

    transaction.customer.credit += transaction.credit
    transaction.customer.save()

payment_was_successful.connect(confirm_transaction)

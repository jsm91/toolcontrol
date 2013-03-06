# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from customers.models import Customer, Transaction

class Command(BaseCommand):
    help = 'Deducts the monthly subscription fee from every customer'

    def handle(self, *args, **options):
        for customer in Customer.objects.filter(is_active=True):
            customer.credit -= customer.subscription_price
            customer.save()

            transaction = Transaction(customer=customer, 
                                      credit = - customer.subscription_price,
                                      description = 'Månedligt abonnement',
                                      is_confirmed=True)
            transaction.save()
            
            if customer.credit < 0:
                for admin in customer.employee_set.filter(is_admin=True):
                    subject = 'Din ToolControl-konto er i minus'
                    message = ('Hej %s\n\n Kontoen for %s på ToolControl er gået i minus (%s kr.). Systemet fungerer stadig, men vi beder dig om at bringe kontoen i plus inden for nærmeste fremtid.\n\n MVH\n ToolControl' % (admin.name, customer.name, customer.credit))
                    admin.send_message(subject, message)

# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from admin.models import Customer
from tools.models import Employee

class Command(BaseCommand):
    help = 'Creates a new customer and an admin for that customer'

    def handle(self,*args, **options):
        customer = Customer.objects.create(name=args[0])

        employee = Employee(name=args[1], is_admin=True, customer=customer,
                            phone_number=args[2])
        employee.set_password('skiftmig')
        employee.save()

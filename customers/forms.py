# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django import forms

from customers.models import Customer
from tools.models import Employee

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ('sms_sent',)    

class CreateCustomerForm(forms.ModelForm):
    administrator = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.IntegerField()

    class Meta:
        model = Customer
        exclude = ('sms_sent',)

    def save(self, commit=True):
        customer = super(CustomerForm, self).save(commit=commit)

        employee = Employee(name=self.cleaned_data['administrator'],
                            email = self.cleaned_data['email'],
                            phone_number=self.cleaned_data['phone_number'],
                            customer=customer,
                            is_admin=True)

        password = Employee.objects.make_random_password()
        employee.set_password(password)
        employee.save()

        message = ('Hej ' + employee.name + '\n\n' + 
                   'Du er netop blevet oprettet i ToolControl-systemet ' +
                   'hos ' + customer.name + '. Du kan logge ind med navnet ' +
                   employee.name + ' samt kodeordet ' + password + '. ' +
                   'Kodeordet kan ændres når du er logget ind.\n\n' +
                   'MVH\n' +
                   'ToolControl')
        
        employee.send_mail('Oprettet som bruger', message)
        employee.send_sms(message)

        return customer
        

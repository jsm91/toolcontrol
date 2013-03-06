# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.db.models import Q

from customers.models import Customer, Transaction
from tools.models import Employee, Ticket, TicketAnswer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ('sms_sent',)    

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['duplicate'].queryset = Ticket.objects.filter(~Q(id=self.initial['id']), duplicate__isnull=True)
        self.fields['assigned_to'].queryset = Employee.objects.filter(customer__isnull=True)

    def save(self, commit=True):
        ticket = super(TicketForm,self).save(commit=commit)

        if ticket.duplicate:
            for duplicate in ticket.ticket_set.all():
                duplicate.duplicate = ticket.duplicate
                duplicate.save()

        for duplicate in ticket.ticket_set.all():
            duplicate.is_open = ticket.is_open
            duplicate.save()

        return ticket

class TicketAnswerForm(forms.ModelForm):
    class Meta:
        model = TicketAnswer
        fields = ['text',]

class CreateTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        exclude = ('duplicate', 'is_open', 'created_by',)

    def __init__(self, *args, **kwargs):
        super(CreateTicketForm, self).__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = Employee.objects.filter(customer__isnull=True)

class AccountCreateTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        exclude = ('duplicate', 'is_open', 'created_by', 'reported_by',
                   'assigned_to')

class CreateCustomerForm(forms.ModelForm):
    administrator = forms.CharField(label='Navn på administrator')
    email = forms.EmailField()
    phone_number = forms.IntegerField(label='Telefonnummer')

    class Meta:
        model = Customer
        exclude = ('sms_sent',)

    def save(self, commit=True):
        customer = super(CreateCustomerForm, self).save(commit=commit)

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
        
        employee.send_message('Oprettet som bruger', message)

        return customer
        
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields=['credit',]

    def clean(self):
        cleaned_data = super(TransactionForm, self).clean()

        if cleaned_data.get('credit'):
            if cleaned_data['credit'] <= 0:
                raise forms.ValidationError('Beløbet skal være positivt')

        return cleaned_data

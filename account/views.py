# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import datetime, logging
logger = logging.getLogger(__name__)

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, DetailView, FormView, ListView

from customers.forms import AccountCreateTicketForm, TransactionForm
from customers.forms import TicketAnswerForm
from customers.models import FAQPost, Transaction
from tools.models import Event, Login, Ticket

class HasNoCustomerIsNotAdminRedirectMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.customer:
            return HttpResponseRedirect(reverse('admin_index'))
        elif not request.user.is_admin:
            return HttpResponseRedirect(reverse('index'))
        else:
            return super(HasNoCustomerIsNotAdminRedirectMixin, 
                         self).dispatch(request, *args, **kwargs)

# Index view
class AccountDetail(HasNoCustomerIsNotAdminRedirectMixin, DetailView):
    template_name='customers/account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountDetail, self).get_context_data(**kwargs)

        context['logins'] = Login.objects.filter(employee__customer=self.object, timestamp__gte=datetime.datetime.now() - datetime.timedelta(days = 1)).count()
        context['events'] = Event.objects.filter(tool__model__category__customer=self.object, start_date__gte=datetime.datetime.now() - datetime.timedelta(days = 1)).count()

        return context

    def get_object(self, queryset=None):
        return self.request.user.customer

# Transaction views
class CreateTransaction(HasNoCustomerIsNotAdminRedirectMixin, CreateView):
    model = Transaction
    form_class = TransactionForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.customer = self.request.user.customer
        self.object.description = 'Indbetaling via PayPal'
        self.object.save()
        logger.info('Transaction #%s (%s kr.) created by %s' % (self.object.pk, self.object.credit, self.request.user))

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('transaction_detail', args=[self.object.pk])

class TransactionDetail(HasNoCustomerIsNotAdminRedirectMixin, DetailView):
    model = Transaction

    def get_context_data(self, **kwargs):
        context = super(TransactionDetail, self).get_context_data(**kwargs)

        paypal_dict = {
            'currency_code': 'DKK',
            'business': 'kontakt@toolcontrol.dk',
            'amount': self.object.credit_with_fee(),
            'item_name': 'Indbetaling til ToolControl',
            'invoice': self.object.pk,
            'notify_url': 'http://www.toolcontrol.dk/account/transaction/notify',
            'return_url': 'http://www.toolcontrol.dk/account/',
            'cancel_return': 'http://www.toolcontrol.dk/account/transaction/cancel',
            }

        form = PayPalPaymentsForm(initial = paypal_dict)
        context['form'] = form

        return context

# Ticket views
class AccountTicketList(HasNoCustomerIsNotAdminRedirectMixin, ListView):
    template_name = 'customers/account_ticket_list.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return HttpResponseRedirect(reverse('index'))
        else:
            return super(AccountTicketList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        customer = self.request.user.customer

        return Ticket.objects.filter(reported_by=customer).order_by('-is_open', 'duplicate', '-pk')

class AccountCreateTicket(HasNoCustomerIsNotAdminRedirectMixin, CreateView):
    form_class = AccountCreateTicketForm
    template_name='customers/account_ticket_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.reported_by = self.request.user.customer
        self.object.save()
        logger.info('Ticket #%s created (%s) by %s' % (self.object.pk, self.object.name, self.request.user))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('account_ticket_detail', args=[self.object.pk])

class AccountTicketDetail(HasNoCustomerIsNotAdminRedirectMixin, FormView):
    form_class = TicketAnswerForm
    template_name='customers/account_ticket_detail.html'

    def form_valid(self, form):
        ticket_answer = form.save(commit=False)
        ticket = get_object_or_404(Ticket, id = self.kwargs['pk'])
        ticket_answer.ticket = ticket
        ticket_answer.created_by = self.request.user
        ticket_answer.save()
        logger.info('Answer to ticket #%s created by %s' % (ticket.pk, self.request.user))
        return super(AccountTicketDetail, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, id = self.kwargs['pk'])

        if (request.user.customer != ticket.reported_by):
            return HttpResponseRedirect(reverse('index'))

        return super(AccountTicketDetail, 
                     self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AccountTicketDetail, self).get_context_data(**kwargs)
        context['ticket'] = get_object_or_404(Ticket, id = self.kwargs['pk'])

        return context

    def get_success_url(self):
        return reverse('account_ticket_detail', args=[self.kwargs['pk']])

# FAQ views
class AccountFAQList(ListView):
    model = FAQPost
    template_name = 'customers/account_faqpost_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.customer:
            return HttpResponseRedirect(reverse('admin_index'))
        else:
            return super(AccountFAQList, 
                         self).dispatch(request, *args, **kwargs)

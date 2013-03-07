# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import codecs, datetime, logging
logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, FormView, ListView
from django.views.generic import TemplateView, UpdateView

from customers.forms import CreateTicketForm, TicketAnswerForm
from customers.forms import CreateCustomerForm, CustomerForm, TicketForm
from customers.forms import AdminTransactionForm
from customers.models import Customer, FAQCategory, FAQPost, Transaction
from tools.models import Event, Login, Ticket, TicketAnswer, Tool, ToolModel

class HasCustomerRedirectMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.customer:
            return HttpResponseRedirect(reverse('index'))
        else:
            return super(HasCustomerRedirectMixin, 
                         self).dispatch(request, *args, **kwargs)

# Index view
class IndexTemplate(HasCustomerRedirectMixin, TemplateView):
    template_name = 'customers/admin_index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexTemplate, self).get_context_data(**kwargs)

        context['logins'] = Login.objects.filter(timestamp__gte=datetime.datetime.now() - datetime.timedelta(days = 1)).count()
        context['events'] = Event.objects.filter(start_date__gte=datetime.datetime.now() - datetime.timedelta(days = 1)).count()
        context['tickets'] = Ticket.objects.filter(is_open=True, assigned_to=self.request.user)
        context['answers'] = TicketAnswer.objects.filter(is_read=False, ticket__assigned_to=self.request.user)
        context['transactions'] = Transaction.objects.filter(is_confirmed=False)

        return context

# Customer views
class CustomerList(HasCustomerRedirectMixin, ListView):
    model = Customer

class CreateCustomer(HasCustomerRedirectMixin, CreateView):
    model = Customer
    form_class = CreateCustomerForm

class CustomerDetail(HasCustomerRedirectMixin, FormView):
    form_class = AdminTransactionForm
    template_name='customers/customer_detail.html'

    def form_valid(self, form):
        transaction = form.save(commit=False)
        customer = get_object_or_404(Customer, id = self.kwargs['pk'])

        transaction.customer = customer
        transaction.save()

        if transaction.is_confirmed:
            customer.credit += transaction.credit
            customer.save()

        logger.info('Transaction (%s kr for %s) created by %s' % (transaction.credit, customer, self.request.user))
        return super(CustomerDetail, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CustomerDetail, self).get_context_data(**kwargs)
        customer = get_object_or_404(Customer, id = self.kwargs['pk'])

        context['customer'] = customer
        context['tools'] = Tool.objects.filter(model__category__customer=customer)
        context['models'] = ToolModel.objects.filter(category__customer=customer)
        context['categories'] = customer.toolcategory_set.all()
        context['employees'] = customer.employee_set.all()
        context['construction_sites'] = customer.constructionsite_set.all()
        context['containers'] = customer.container_set.all()

        return context

    def get_success_url(self):
        return reverse('customer_detail', args=[self.kwargs['pk']])

class UpdateCustomer(HasCustomerRedirectMixin, UpdateView):
    model = Customer
    form_class = CustomerForm

# Ticket views
class TicketList(HasCustomerRedirectMixin, ListView):
    template_name = 'customers/ticket_list.html'

    def get_queryset(self):
        customer_id = self.request.GET.get('customer')

        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
            return Ticket.objects.filter(reported_by=customer).order_by('-is_open', 'duplicate', '-pk')
        else:
            return Ticket.objects.all().order_by('-is_open', 'duplicate', '-pk')

class CreateTicket(HasCustomerRedirectMixin, CreateView):
    form_class = CreateTicketForm
    template_name='customers/ticket_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        logger.info('Ticket #%s created (%s) by %s' % (self.object.pk, self.object.name, self.request.user))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('ticket_detail', args=[self.object.pk])

class TicketDetail(HasCustomerRedirectMixin, FormView):
    form_class = TicketAnswerForm
    template_name='customers/ticket_detail.html'

    def form_valid(self, form):
        ticket_answer = form.save(commit=False)
        ticket = get_object_or_404(Ticket, id = self.kwargs['pk'])
        ticket_answer.ticket = ticket
        ticket_answer.created_by = self.request.user
        ticket_answer.save()
        logger.info('Answer to ticket #%s created by %s' % (ticket.pk, self.request.user))
        return super(TicketDetail, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, id = self.kwargs['pk'])

        if self.request.user == ticket.assigned_to:
            for answer in ticket.ticketanswer_set.filter(is_read=False):
                logger.info('Answer #%s marked as read by %s' % (answer.pk, self.request.user))
                answer.is_read = True
                answer.save()

        if (request.user.customer and 
            request.user.customer != ticket.reported_by):
            return HttpResponseRedirect(reverse('index'))

        return super(TicketDetail, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TicketDetail, self).get_context_data(**kwargs)
        context['ticket'] = get_object_or_404(Ticket, id = self.kwargs['pk'])

        return context

    def get_success_url(self):
        return reverse('ticket_detail', args=[self.kwargs['pk']])

class UpdateTicket(HasCustomerRedirectMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name='customers/ticket_form.html'

# FAQ views
class FAQList(HasCustomerRedirectMixin, ListView):
    model = FAQPost

class CreateFAQ(HasCustomerRedirectMixin, CreateView):
    model = FAQPost

    def get_success_url(self):
        return reverse('faqpost_list',)

class UpdateFAQ(HasCustomerRedirectMixin, UpdateView):
    model=FAQPost

    def get_success_url(self):
        return reverse('faqpost_list',)

# FAQ category views
class CreateFAQCategory(HasCustomerRedirectMixin, CreateView):
    model = FAQCategory

    def get_success_url(self):
        return reverse('faqpost_list',)

class UpdateFAQCategory(HasCustomerRedirectMixin, UpdateView):
    model=FAQCategory

    def get_success_url(self):
        return reverse('faqpost_list',)

# Action view
@login_required
def action(request):
    logger.info('%s is initiating an action' % request.user)

    if request.user.customer:
        logger.warning('Action aborted, user is not admin')
        return HttpResponseRedirect(reverse('index'))

    if 'close_ticket' in request.POST:
        ticket_id = request.POST.get('close_ticket')
        ticket = get_object_or_404(Ticket, id = ticket_id)
        ticket.is_open = False
        ticket.save()

        for duplicate in ticket.ticket_set.all():
            duplicate.is_open = False
            duplicate.save()

        logger.info('Ticket #%s has been closed' % ticket_id)

        return HttpResponseRedirect(reverse('ticket_detail', 
                                            args=[ticket_id]))
    elif 'reopen_ticket' in request.POST:
        ticket_id = request.POST.get('reopen_ticket')
        ticket = get_object_or_404(Ticket, id = ticket_id)
        ticket.is_open = True
        ticket.save()

        for duplicate in ticket.ticket_set.all():
            duplicate.is_open = True
            duplicate.save()

        logger.info('Ticket #%s has been reopened' % ticket_id)

        return HttpResponseRedirect(reverse('ticket_detail', 
                                            args=[ticket_id]))
    elif 'delete_ticket' in request.POST:
        ticket_id = request.POST.get('delete_ticket')
        ticket = get_object_or_404(Ticket, id = ticket_id)
        ticket.delete()

        logger.info('Ticket #%s has been deleted' % ticket_id)

        return HttpResponseRedirect(reverse('ticket_list'))

    elif 'confirm_transaction' in request.POST:
        transaction_id = request.POST.get('confirm_transaction')
        transaction = get_object_or_404(Transaction, id = transaction_id)
        transaction.is_confirmed = True
        transaction.save()

        transaction.customer.credit += transaction.credit
        transaction.customer.save()

        logger.info('Transaction #%s has been confirmed' % transaction_id)

        return HttpResponseRedirect(reverse('admin_index'))

    elif 'delete_transaction' in request.POST:
        transaction_id = request.POST.get('delete_transaction')
        transaction = get_object_or_404(Transaction, id = transaction_id)
        transaction.delete()

        logger.info('Transaction #%s has been deleted' % transaction_id)

        return HttpResponseRedirect(reverse('admin_index'))

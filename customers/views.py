# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import codecs, datetime, logging
logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, DetailView, FormView, ListView
from django.views.generic import TemplateView, UpdateView

from customers.forms import CreateTicketForm, TicketAnswerForm, TransactionForm
from customers.forms import AccountCreateTicketForm
from customers.models import Customer, Transaction
from paypal.standard.forms import PayPalPaymentsForm
from tools.models import Event, Login, Ticket, TicketAnswer, Tool, ToolModel

class CreateViewWithRedirection(CreateView):
    def get(self, request, *args, **kwargs):
        if request.user.customer:
            return HttpResponseRedirect(reverse('index'))
        else:
            return super(CreateViewWithRedirection, 
                         self).get(request, *args, **kwargs)

class DetailViewWithRedirection(DetailView):
    def get(self, request, *args, **kwargs):
        if request.user.customer:
            return HttpResponseRedirect(reverse('index'))
        else:
            return super(DetailViewWithRedirection, 
                         self).get(request, *args, **kwargs)

class FormViewWithRedirection(FormView):
    def get(self, request, *args, **kwargs):
        if request.user.customer:
            return HttpResponseRedirect(reverse('index'))
        else:
            return super(FormViewWithRedirection, 
                         self).get(request, *args, **kwargs)

class ListViewWithRedirection(ListView):
    def get(self, request, *args, **kwargs):
        if request.user.customer:
            return HttpResponseRedirect(reverse('index'))
        else:
            return super(ListViewWithRedirection, 
                         self).get(request, *args, **kwargs)

class TemplateViewWithRedirection(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.customer:
            return HttpResponseRedirect(reverse('index'))
        else:
            return super(TemplateViewWithRedirection, 
                         self).get(request, *args, **kwargs)

class UpdateViewWithRedirection(UpdateView):
    def get(self, request, *args, **kwargs):
        if request.user.customer:
            return HttpResponseRedirect(reverse('index'))
        else:
            return super(UpdateViewWithRedirection, 
                         self).get(request, *args, **kwargs)

class IndexTemplate(TemplateViewWithRedirection):
    template_name = 'customers/admin_index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexTemplate, self).get_context_data(**kwargs)

        context['logins'] = Login.objects.filter(timestamp__gte=datetime.datetime.now() - datetime.timedelta(days = 1)).count()
        context['events'] = Event.objects.filter(start_date__gte=datetime.datetime.now() - datetime.timedelta(days = 1)).count()
        context['tickets'] = Ticket.objects.filter(is_open=True, assigned_to=self.request.user)
        context['answers'] = TicketAnswer.objects.filter(is_read=False, ticket__assigned_to=self.request.user)
        context['transactions'] = Transaction.objects.filter(is_confirmed=False)

        return context

class CustomerDetail(DetailViewWithRedirection):
    model = Customer

    def get_context_data(self, **kwargs):
        context = super(CustomerDetail, self).get_context_data(**kwargs)

        context['tools'] = Tool.objects.filter(model__category__customer=self.object)
        context['models'] = ToolModel.objects.filter(category__customer=self.object)
        context['categories'] = self.object.toolcategory_set.all()
        context['employees'] = self.object.employee_set.all()
        context['construction_sites'] = self.object.constructionsite_set.all()
        context['containers'] = self.object.container_set.all()

        return context

class TicketList(ListViewWithRedirection):
    template_name = 'customers/ticket_list.html'

    def get_queryset(self):
        customer_id = self.request.GET.get('customer')

        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
            return Ticket.objects.filter(reported_by=customer).order_by('-is_open', 'duplicate', '-pk')
        else:
            return Ticket.objects.all().order_by('-is_open', 'duplicate', '-pk')

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

class TicketDetail(FormViewWithRedirection):
    form_class = TicketAnswerForm
    template_name='customers/ticket_detail.html'

    def form_valid(self, form):
        ticket_answer = form.save(commit=False)
        ticket = get_object_or_404(Ticket, id = self.kwargs['pk'])
        ticket_answer.ticket = ticket
        ticket_answer.created_by = self.request.user
        ticket_answer.save()
        return super(TicketDetail, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, id = self.kwargs['pk'])

        if self.request.user == ticket.assigned_to:
            for answer in ticket.ticketanswer_set.all():
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

class CreateTicket(CreateViewWithRedirection):
    form_class = CreateTicketForm
    template_name='customers/ticket_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('ticket_detail', args=[self.object.pk])

class AccountDetail(DetailView):
    template_name='customers/account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountDetail, self).get_context_data(**kwargs)

        context['logins'] = Login.objects.filter(employee__customer=self.object, timestamp__gte=datetime.datetime.now() - datetime.timedelta(days = 1)).count()
        context['events'] = Event.objects.filter(tool__model__category__customer=self.object, start_date__gte=datetime.datetime.now() - datetime.timedelta(days = 1)).count()

        return context

    def get_object(self, queryset=None):
        return self.request.user.customer

def account_ticket_list(request):
    return None

def payment(request):
    return None

class CreateTransaction(CreateView):
    model = Transaction
    form_class = TransactionForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.customer = self.request.user.customer
        self.object.description = 'Indbetaling via PayPal'
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('paypal', args=[self.object.pk])

class TransactionDetail(DetailView):
    model = Transaction

    def get_context_data(self, **kwargs):
        context = super(TransactionDetail, self).get_context_data(**kwargs)

        paypal_dict = {
            'currency_code': 'DKK',
            'business': 'kontakt@toolcontrol.dk',
            'amount': round((self.object.credit + 2.6) / 0.966, 2),
            'item_name': 'Indbetaling til ToolControl',
            'invoice': self.object.pk,
            'notify_url': 'http://www.skou.toolcontrol.dk/admin/payment/notify',
            'return_url': 'http://www.skou.toolcontrol.dk/admin/account',
            'cancel_return': 'http://www.skou.toolcontrol.dk/admin/payment/cancel',
            }

        form = PayPalPaymentsForm(initial=paypal_dict)
        context['form'] = form

        return context

class AccountTicketList(ListView):
    template_name = 'customers/account_ticket_list.html'

    def get_queryset(self):
        customer = self.request.user.customer

        return Ticket.objects.filter(reported_by=customer).order_by('-is_open', 'duplicate', '-pk')

class AccountCreateTicket(CreateView):
    form_class = AccountCreateTicketForm
    template_name='customers/account_ticket_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.reported_by = self.request.user.customer
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('account_ticket_detail', args=[self.object.pk])

class AccountTicketDetail(FormView):
    form_class = TicketAnswerForm
    template_name='customers/account_ticket_detail.html'

    def form_valid(self, form):
        ticket_answer = form.save(commit=False)
        ticket = get_object_or_404(Ticket, id = self.kwargs['pk'])
        ticket_answer.ticket = ticket
        ticket_answer.created_by = self.request.user
        ticket_answer.save()
        return super(AccountTicketDetail, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, id = self.kwargs['pk'])

        if (request.user.customer and 
            request.user.customer != ticket.reported_by):
            return HttpResponseRedirect(reverse('index'))

        return super(AccountTicketDetail, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AccountTicketDetail, self).get_context_data(**kwargs)
        context['ticket'] = get_object_or_404(Ticket, id = self.kwargs['pk'])

        return context

    def get_success_url(self):
        return reverse('account_ticket_detail', args=[self.kwargs['pk']])

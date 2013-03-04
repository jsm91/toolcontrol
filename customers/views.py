# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import codecs

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, DetailView, FormView, ListView
from django.views.generic import TemplateView, UpdateView

from customers.forms import CreateTicketForm, TicketAnswerForm
from customers.models import Customer
from tools.models import Ticket, Tool, ToolModel

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
            return Ticket.objects.filter(reported_by=customer).order_by('-is_open', '-pk')
        else:
            return Ticket.objects.all().order_by('-is_open', '-pk')

@login_required
def action(request):
    if request.user.customer:
        return HttpResponseRedirect(reverse('index'))

    if 'close_ticket' in request.POST:
        ticket_id = request.POST.get('close_ticket')
        ticket = get_object_or_404(Ticket, id = ticket_id)
        ticket.is_open = False
        ticket.save()
        return HttpResponseRedirect(reverse('ticket_detail', 
                                            args=[ticket_id]))
    elif 'reopen_ticket' in request.POST:
        ticket_id = request.POST.get('reopen_ticket')
        ticket = get_object_or_404(Ticket, id = ticket_id)
        ticket.is_open = True
        ticket.save()
        return HttpResponseRedirect(reverse('ticket_detail', 
                                            args=[ticket_id]))
    elif 'delete_ticket' in request.POST:
        ticket_id = request.POST.get('delete_ticket')
        ticket = get_object_or_404(Ticket, id = ticket_id)
        ticket.delete()
        return HttpResponseRedirect(reverse('ticket_list'))

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

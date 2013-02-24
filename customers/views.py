# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import codecs

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, FormView, ListView

from customers.forms import TicketAnswerForm
from customers.models import Customer
from tools.models import Ticket, Tool, ToolModel

class CustomerDetail(DetailView):
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

class TicketList(ListView):
    template_name = 'customers/ticket_list.html'

    def get_queryset(self):
        customer_id = self.request.GET.get('customer')

        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
            return Ticket.objects.filter(reported_by=customer)
        else:
            return Ticket.objects.all()

def action(request):
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

class TicketDetail(FormView):
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

def log(request):
    log = ''
    search = request.POST.get('search')

    f = codecs.open('log.log', encoding='utf-8')
    line = f.readline()

    while line:
        if search:
            if search.lower() in line.lower():
                log += "%s<br>" % line
        else:
            log += "%s<br>" % line
            
        line = f.readline()

    return render(request, 'customers/log.html', {'log': log, 
                                                  'search': search})

# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import codecs

from django.shortcuts import render
from django.views.generic import DetailView

from customers.models import Customer
from tools.models import Tool, ToolModel

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

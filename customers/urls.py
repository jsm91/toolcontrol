from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.views.generic import UpdateView

from customers.forms import CustomerForm, CreateCustomerForm, CreateTicketForm, TicketForm
from customers.models import Customer
from customers.views import CreateTicket, CustomerDetail, TicketDetail
from customers.views import TicketList
from tools.models import Ticket

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('customers.views',
    url(r'^$', 
        login_required(TemplateView.as_view(template_name = 
                                            'customers/admin_index.html')),
        name='admin_index'),
    url(r'customers/$', login_required(ListView.as_view(model=Customer)), 
        name='customer_list'),
    url(r'customers/create$', 
        login_required(CreateView.as_view(model=Customer, 
                                          form_class=CreateCustomerForm)), 
        name='customer_create'),
    url(r'customers/(?P<pk>\d+)/$', 
        login_required(CustomerDetail.as_view()),
        name='customer_detail'),
    url(r'customers/(?P<pk>\d+)/update/$', 
        login_required(UpdateView.as_view(model=Customer, 
                                          form_class=CustomerForm)), 
        name='customer_update'),

    url(r'tickets/$', login_required(TicketList.as_view()), 
        name='ticket_list'),
    url(r'tickets/create$', login_required(CreateTicket.as_view()), 
        name='ticket_create'),
    url(r'tickets/(?P<pk>\d+)/$', login_required(TicketDetail.as_view()), 
        name='ticket_detail'),
    url(r'tickets/(?P<pk>\d+)/update/$', 
        login_required(UpdateView.as_view(model=Ticket, form_class=TicketForm, template_name='customers/ticket_form.html')), 
        name='ticket_update'),

    url(r'action/$', 'action', name='action'),
   
    # Examples:
    # url(r'^$', 'sidste.views.home', name='home'),
    # url(r'^sidste/', include('sidste.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

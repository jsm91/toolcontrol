from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy

from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.views.generic import UpdateView

from customers.forms import CustomerForm, CreateCustomerForm, CreateTicketForm, TicketForm, TransactionForm
from customers.models import Customer, FAQCategory, FAQPost, Transaction

from customers.views import AccountDetail, CreateTransaction

from customers.views import CreateTicket, CustomerDetail, TicketDetail
from customers.views import IndexTemplate, TicketList, TransactionDetail
from customers.views import AccountTicketList, AccountCreateTicket
from customers.views import AccountTicketDetail, CustomerList, CreateCustomer
from customers.views import UpdateCustomer, UpdateTicket

from customers.views import FAQList, CreateFAQ, UpdateFAQ
from customers.views import CreateFAQCategory, UpdateFAQCategory

from tools.models import Ticket

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('customers.views',
    url(r'^$', login_required(IndexTemplate.as_view()), name = 'admin_index'),

    # Customer URL's
    url(r'^customers/$', login_required(CustomerList.as_view()), 
        name='customer_list'),
    url(r'^customers/create$', login_required(CreateCustomer.as_view()), 
        name='customer_create'),
    url(r'^customers/(?P<pk>\d+)/$', login_required(CustomerDetail.as_view()),
        name='customer_detail'),
    url(r'^customers/(?P<pk>\d+)/update/$', login_required(UpdateCustomer.as_view()), 
        name='customer_update'),

    # Ticket URL's
    url(r'^tickets/$', login_required(TicketList.as_view()), 
        name='ticket_list'),
    url(r'^tickets/create$', login_required(CreateTicket.as_view()), 
        name='ticket_create'),
    url(r'^tickets/(?P<pk>\d+)/$', login_required(TicketDetail.as_view()), 
        name='ticket_detail'),
    url(r'^tickets/(?P<pk>\d+)/update/$', login_required(UpdateTicket.as_view()), 
        name='ticket_update'),

    # FAQ URL's
    url(r'^faq/$', login_required(FAQList.as_view()), name='faqpost_list'),
    url(r'^faq/create$', login_required(CreateFAQ.as_view()), name='faqpost_create'),
    url(r'^faq/(?P<pk>\d+)/update/$', login_required(UpdateFAQ.as_view()),
        name='faqpost_update'),

    # FAQ category URL's
    url(r'^faq-category/create/$', login_required(CreateFAQCategory.as_view()), 
        name='faqcategory_create'),
    url(r'^faq-category/(?P<pk>\d+)/update$', login_required(UpdateFAQCategory.as_view()),
        name='faqcategory_update'),

    # Action URL
    url(r'action/$', 'action', name='action'),

    url(r'^account/$', login_required(AccountDetail.as_view()), 
        name='account'),
    url(r'^payment/$', login_required(CreateTransaction.as_view()), 
        name='payment'),
    url(r'^payment/(?P<pk>\d+)/$', login_required(TransactionDetail.as_view()),
        name='transaction_detail'),
    (r'^payment/notify/', include('paypal.standard.ipn.urls')),

    url(r'account/tickets/$', login_required(AccountTicketList.as_view()), 
        name='account_ticket_list'),
    url(r'account/tickets/create$', 
        login_required(AccountCreateTicket.as_view()), 
        name='account_ticket_create'),
    url(r'^account/tickets/(?P<pk>\d+)/$', 
        login_required(AccountTicketDetail.as_view()), 
        name='account_ticket_detail'),

    url(r'^account/faq/$', 
        login_required(ListView.as_view(model=FAQPost, template_name='customers/account_faqpost_list.html')), name='account_faqpost_list'),

   
    # Examples:
    # url(r'^$', 'sidste.views.home', name='home'),
    # url(r'^sidste/', include('sidste.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

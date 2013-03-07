from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from customers.views import IndexTemplate, CustomerList, CreateCustomer
from customers.views import CustomerDetail, UpdateCustomer, TicketList
from customers.views import CreateTicket, TicketDetail, UpdateTicket
from customers.views import FAQList, CreateFAQ, UpdateFAQ
from customers.views import CreateFAQCategory, UpdateFAQCategory

urlpatterns = patterns('customers.views',
    # Index URL
    url(r'^$', login_required(IndexTemplate.as_view()), name = 'admin_index'),

    # Customer URL's
    url(r'^customers/$', login_required(CustomerList.as_view()), 
        name='customer_list'),
    url(r'^customers/create$', login_required(CreateCustomer.as_view()), 
        name='customer_create'),
    url(r'^customers/(?P<pk>\d+)/$', login_required(CustomerDetail.as_view()),
        name='customer_detail'),
    url(r'^customers/(?P<pk>\d+)/update/$', 
        login_required(UpdateCustomer.as_view()), name='customer_update'),

    # Ticket URL's
    url(r'^tickets/$', login_required(TicketList.as_view()), 
        name='ticket_list'),
    url(r'^tickets/create$', login_required(CreateTicket.as_view()), 
        name='ticket_create'),
    url(r'^tickets/(?P<pk>\d+)/$', login_required(TicketDetail.as_view()), 
        name='ticket_detail'),
    url(r'^tickets/(?P<pk>\d+)/update/$', 
        login_required(UpdateTicket.as_view()), name='ticket_update'),

    # FAQ URL's
    url(r'^faq/$', login_required(FAQList.as_view()), name='faqpost_list'),
    url(r'^faq/create$', login_required(CreateFAQ.as_view()), 
        name='faqpost_create'),
    url(r'^faq/(?P<pk>\d+)/update/$', login_required(UpdateFAQ.as_view()),
        name='faqpost_update'),

    # FAQ category URL's
    url(r'^faq-category/create/$', login_required(CreateFAQCategory.as_view()),
        name='faqcategory_create'),
    url(r'^faq-category/(?P<pk>\d+)/update$', 
        login_required(UpdateFAQCategory.as_view()),
        name='faqcategory_update'),

    # Action URL
    url(r'action/$', 'action', name='action'),
)

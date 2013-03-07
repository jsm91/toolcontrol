from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from account.views import AccountDetail
from account.views import CreateTransaction, TransactionDetail
from account.views import AccountTicketList, AccountCreateTicket
from account.views import AccountTicketDetail, AccountFAQList

urlpatterns = patterns('',
    # Index URL
    url(r'^$', login_required(AccountDetail.as_view()), name='account'),

    # Transaction URL's
    url(r'^transaction/$', login_required(CreateTransaction.as_view()), 
        name='create_transaction'),
    url(r'^transaction/(?P<pk>\d+)/$', 
        login_required(TransactionDetail.as_view()), 
        name='transaction_detail'),
    (r'^transaction/notify/', include('paypal.standard.ipn.urls')),

    # Ticket URL's
    url(r'tickets/$', login_required(AccountTicketList.as_view()), 
        name='account_ticket_list'),
    url(r'tickets/create$', login_required(AccountCreateTicket.as_view()), 
        name='account_ticket_create'),
    url(r'^tickets/(?P<pk>\d+)/$', 
        login_required(AccountTicketDetail.as_view()), 
        name='account_ticket_detail'),

    # FAQ URL's
    url(r'^faq/$', login_required(AccountFAQList.as_view()), 
        name='account_faqpost_list'),
)

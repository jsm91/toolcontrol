from django.conf.urls import patterns, include, url

from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.views.generic import UpdateView

from customers.forms import CustomerForm, CreateCustomerForm
from customers.models import Customer
from customers.views import CustomerDetail

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('customers.views',
    url(r'^$', 
        TemplateView.as_view(template_name='customers/admin_index.html'),
        name='admin_index'),
    url(r'customers/$', ListView.as_view(model=Customer), 
        name='customer_list'),
    url(r'customers/create$', 
        CreateView.as_view(model=Customer, form_class=CreateCustomerForm), 
        name='customer_create'),
    url(r'customers/(?P<pk>\d+)/$', 
        CustomerDetail.as_view(),
        name='customer_detail'),
    url(r'customers/(?P<pk>\d+)/update/$', 
        UpdateView.as_view(model=Customer, form_class=CustomerForm), 
        name='customer_update'),
    url(r'log/$', 'log', name='log'),
                    
   
    # Examples:
    # url(r'^$', 'sidste.views.home', name='home'),
    # url(r'^sidste/', include('sidste.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

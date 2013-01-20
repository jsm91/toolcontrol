from django.conf.urls import patterns, include, url

from tools.models import ConstructionSite, Employee, Tool, ToolCategory
from tools.models import ToolModel

from tools.views import CategoryListView, ConstructionSiteListView 
from tools.views import EventListView, EmployeeListView, LoanListView
from tools.views import ModelListView, SimpleToolListView, ToolListView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('tools.views',
    url(r'^$', 'index', name='index'),
    url(r'^login/$', 'login_view', name='login'),
    url(r'^logout/$', 'logout_view', name='logout'),
    url(r'^stats/$', 'stats', name='stats'),
    url(r'^settings/$', 'settings', name='settings'),

    # AJAX requests for objects
    url(r'^model_object/$', 'model_object', name='model_object'),

    # AJAX requests for lists
    url(r'^tool_list/$', ToolListView.as_view(), name='tool_list'),
    url(r'^model_list/$', ModelListView.as_view(), name='model_list'),
    url(r'^category_list/$', CategoryListView.as_view(), name='category_list'),
    url(r'^employee_list/$', EmployeeListView.as_view(), name='employee_list'),
    url(r'^building_site_list/$', ConstructionSiteListView.as_view(),
        name='building_site_list'),
    url(r'^event_list/$', EventListView.as_view(), name='event_list'),
    url(r'^loan_list/$', LoanListView.as_view(), name='loan_list'),
    url(r'^simple_tool_list/$', SimpleToolListView.as_view(), 
        name='simple_tool_list'),

    # AJAX requests for banners
    url(r'^tool_banner/$', 'tool_banner', name='tool_banner'),
    url(r'^model_banner/$', 'model_banner', name='model_banner'),
    url(r'^category_banner/$', 'category_banner', name='category_banner'),
    url(r'^employee_banner/$', 'employee_banner', name='employee_banner'),
    url(r'^building_site_banner/$', 'building_site_banner', 
        name='building_site_banner'),

    # AJAX requests for forms
    url(r'^tool_form/$', 'tool_form', name='tool_form'),
    url(r'^model_form/$', 'model_form', name='model_form'),
    url(r'^category_form/$', 'category_form', name='category_form'),
    url(r'^employee_form/$', 'employee_form', name='employee_form'),
    url(r'^loan_form/$', 'loan_form', name='loan_form'),
    url(r'^building_site_form/$', 'building_site_form', 
        name='building_site_form'),

    # AJAX requests for actions
    url(r'^tool_action/$', 'tool_action', name='tool_action'),
    url(r'^model_action/$', 'model_action', name='model_action'),
    url(r'^category_action/$', 'category_action', name='category_action'),
    url(r'^employee_action/$', 'employee_action', name='employee_action'),
    url(r'^building_site_action/$', 'construction_site_action', 
        name='building_site_action'),

    # AJAX requests for deletes
    url(r'^tool_delete/$', 'delete', 
        {'class_to_delete': Tool}, name='tool_delete'),
    url(r'^model_delete/$', 'delete', 
        {'class_to_delete': ToolModel}, name='model_delete'),
    url(r'^category_delete/$', 'delete', 
        {'class_to_delete': ToolCategory}, name='category_delete'),
    url(r'^employee_delete/$', 'delete', 
        {'class_to_delete': Employee}, name='employee_delete'),
    url(r'^building_site_delete/$', 'delete', 
        {'class_to_delete': ConstructionSite}, name='building_site_delete'),
    url(r'^event_delete/$', 'event_delete', name='event_delete'),

    # Forgot password
    url(r'^forgot_password/$', 'forgot_password', name='forgot_password'),
    url(r'^reset_password/(?P<token>\w+)$', 'reset_password', name='reset_password'),
)

# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from version2.views import BuildingSiteList, ContainerList, EmployeeList
from version2.views import ToolList, ToolCategoryList, ToolModelList
from version2.views import CreateTool, CreateToolCategory, CreateToolModel
from version2.views import CreateContainer, CreateBuildingSite, CreateEmployee
from version2.views import UpdateTool, UpdateToolCategory, UpdateToolModel
from version2.views import UpdateContainer, UpdateBuildingSite, UpdateEmployee
from version2.views import DeleteTool, DeleteToolCategory, DeleteToolModel
from version2.views import DeleteContainer, DeleteBuildingSite, DeleteEmployee
from version2.views import LoanTools, RepairTools, ReturnTools, ServiceTools
from version2.views import ReserveTools, ScrapTools, LostTools, DeleteTools
from version2.views import DeleteToolModels, DeleteToolCategories
from version2.views import MakeEmployeesActive, MakeEmployeesInactive
from version2.views import MakeEmployeesAdmin, MakeEmployeesNonadmin
from version2.views import MakeEmployeesLoanFlagged, DeleteEmployees
from version2.views import MakeEmployeesNotLoanFlagged, ToolDetails
from version2.views import MakeBuildingSitesActive, MakeBuildingSitesInactive
from version2.views import DeleteBuildingSites, MakeContainersActive
from version2.views import DeleteContainers, MakeContainersInactive

urlpatterns = patterns(
    '',

    url(r'^$', RedirectView.as_view(url=reverse_lazy('tool_list_v2')), 
        name='index'),
    
    # List views
    url(r'^vaerktoej/$', ToolList.as_view(), name='tool_list_v2'),
    url(r'^modeller/$', ToolModelList.as_view(), name='tool_model_list_v2'),
    url(r'^kategorier/$', ToolCategoryList.as_view(), 
        name='tool_category_list_v2'),
    url(r'^medarbejdere/$', EmployeeList.as_view(), name='employee_list_v2'),
    url(r'^byggepladser/$', BuildingSiteList.as_view(), 
        name='building_site_list_v2'),
    url(r'^containere/$', ContainerList.as_view(), name='container_list_v2'),

    # Create views
    url(r'^vaerktoej/ny$', CreateTool.as_view(), name='create_tool_v2'),
    url(r'^modeller/ny$', CreateToolModel.as_view(), 
        name='create_tool_model_v2'),
    url(r'^kategorier/ny$', CreateToolCategory.as_view(), 
        name='create_tool_category_v2'),
    url(r'^medarbejdere/ny$', CreateEmployee.as_view(), 
        name='create_employee_v2'),
    url(r'^byggepladser/ny$', CreateBuildingSite.as_view(), 
        name='create_building_site_v2'),
    url(r'^containere/ny$', CreateContainer.as_view(), 
        name='create_container_v2'),

    # Update views
    url(r'^vaerktoej/(?P<pk>\d+)/rediger/$', UpdateTool.as_view(), 
        name='update_tool_v2'),
    url(r'^modeller/(?P<pk>\d+)/rediger/$', UpdateToolModel.as_view(), 
        name='update_tool_model_v2'),
    url(r'^kategorier/(?P<pk>\d+)/rediger/$', UpdateToolCategory.as_view(), 
        name='update_tool_category_v2'),
    url(r'^medarbejdere/(?P<pk>\d+)/rediger/$', UpdateEmployee.as_view(), 
        name='update_employee_v2'),
    url(r'^byggepladser/(?P<pk>\d+)/rediger/$', UpdateBuildingSite.as_view(), 
        name='update_building_site_v2'),
    url(r'^containere/(?P<pk>\d+)/rediger/$', UpdateContainer.as_view(), 
        name='update_container_v2'),

    # Delete views
    url(r'^vaerktoej/(?P<pk>\d+)/slet/$', DeleteTool.as_view(), 
        name='delete_tool_v2'),
    url(r'^modeller/(?P<pk>\d+)/slet/$', DeleteToolModel.as_view(), 
        name='delete_tool_model_v2'),
    url(r'^kategorier/(?P<pk>\d+)/slet/$', DeleteToolCategory.as_view(), 
        name='delete_tool_category_v2'),
    url(r'^medarbejdere/(?P<pk>\d+)/slet/$', DeleteEmployee.as_view(), 
        name='delete_employee_v2'),
    url(r'^byggepladser/(?P<pk>\d+)/slet/$', DeleteBuildingSite.as_view(), 
        name='delete_building_site_v2'),
    url(r'^containere/(?P<pk>\d+)/slet/$', DeleteContainer.as_view(), 
        name='delete_container_v2'),

    # Action views
    url(r'^vaerktoej/service/$', ServiceTools.as_view(), 
        name='service_tools_v2'),
    url(r'^vaerktoej/udlaan/$', LoanTools.as_view(), 
        name='loan_tools_v2'),
    url(r'^vaerktoej/reparation/$', RepairTools.as_view(), 
        name='repair_tools_v2'),
    url(r'^vaerktoej/returnering/$', ReturnTools.as_view(), 
        name='return_tools_v2'),
    url(r'^vaerktoej/reservation/$', ReserveTools.as_view(), 
        name='reserve_tools_v2'),
    url(r'^vaerktoej/bortkommet/$', LostTools.as_view(), 
        name='lost_tools_v2'),
    url(r'^vaerktoej/kasseret/$', ScrapTools.as_view(), 
        name='scrap_tools_v2'),
    url(r'^vaerktoej/slet/$', DeleteTools.as_view(), 
        name='delete_tools_v2'),
    url(r'^modeller/slet/$', DeleteToolModels.as_view(), 
        name='delete_tool_models_v2'),
    url(r'^kategorier/slet/$', DeleteToolCategories.as_view(), 
        name='delete_tool_categories_v2'),
    url(r'^medarbejdere/aktiv/$', MakeEmployeesActive.as_view(), 
        name='make_employees_active_v2'),
    url(r'^medarbejdere/inaktiv/$', MakeEmployeesInactive.as_view(), 
        name='make_employees_inactive_v2'),
    url(r'^medarbejdere/administrator/$', MakeEmployeesAdmin.as_view(), 
        name='make_employees_admin_v2'),
    url(r'^medarbejdere/fjern-administrator/$', 
        MakeEmployeesNonadmin.as_view(),
        name='make_employees_nonadmin_v2'),
    url(r'^medarbejdere/laaneflag/$', MakeEmployeesLoanFlagged.as_view(), 
        name='make_employees_loan_flagged_v2'),
    url(r'^medarbejdere/fjern-laaneflag/$', 
        MakeEmployeesNotLoanFlagged.as_view(),
        name='make_employees_not_loan_flagged_v2'),
    url(r'^medarbejdere/slet/$', DeleteEmployees.as_view(),
        name='delete_employees_v2'),
    url(r'^byggepladser/aktiv/$', MakeBuildingSitesActive.as_view(), 
        name='make_building_sites_active_v2'),
    url(r'^byggepladser/inaktiv/$', MakeBuildingSitesInactive.as_view(), 
        name='make_building_sites_inactive_v2'),
    url(r'^byggepladser/slet/$', DeleteBuildingSites.as_view(),
        name='delete_building_sites_v2'),
    url(r'^containere/aktiv/$', MakeContainersActive.as_view(), 
        name='make_containers_active_v2'),
    url(r'^containere/inaktiv/$', MakeContainersInactive.as_view(), 
        name='make_containers_inactive_v2'),
    url(r'^containere/slet/$', DeleteContainers.as_view(),
        name='delete_containers_v2'),

    # Detail views
    url(r'^vaerktoej/(?P<pk>\d+)/$', ToolDetails.as_view(), 
        name='tool_details_v2'),    
)

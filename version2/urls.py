# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
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
from version2.views import LoanContainers, ReturnContainers, Settings
from version2.views import ChangePassword, Stats, EmployeeStats, DeleteEvent
from version2.views import DeleteReservation, ToolModelDetails
from version2.views import ToolCategoryDetails, EmployeeDetails
from version2.views import BuildingSiteDetails, ContainerDetails
from version2.views import CreateManyTools, QRAction, QRSuccess, QRTools
from version2.views import LoanToolsSingle, ReserveToolsSingle, LoginView
from version2.views import LogoutView

urlpatterns = patterns(
    'version2.views',

    url(r'^$', RedirectView.as_view(url=reverse_lazy('tool_list_v2')), 
        name='index_v2'),
    url(r'^indstillinger/$', login_required(Settings.as_view()), 
        name='settings_v2'),
    url(r'^skift-kode/$', login_required(ChangePassword.as_view()), 
        name='change_password_v2'),
    url(r'^statistik/$', login_required(Stats.as_view()), 
        name='stats_v2'),
    url(r'^statistik/medarbejdere/$', login_required(EmployeeStats.as_view()), 
        name='employee_stats_v2'),
    url(r'^login/$', LoginView.as_view(), name='login_v2'),
    url(r'^logout/$', LogoutView.as_view(), name='logout_v2'),
    
    # List views
    url(r'^vaerktoej/$', login_required(ToolList.as_view()), 
        name='tool_list_v2'),
    url(r'^modeller/$', login_required(ToolModelList.as_view()), 
        name='tool_model_list_v2'),
    url(r'^kategorier/$', login_required(ToolCategoryList.as_view()), 
        name='tool_category_list_v2'),
    url(r'^medarbejdere/$', login_required(EmployeeList.as_view()), 
        name='employee_list_v2'),
    url(r'^byggepladser/$', login_required(BuildingSiteList.as_view()), 
        name='building_site_list_v2'),
    url(r'^containere/$', login_required(ContainerList.as_view()), 
        name='container_list_v2'),

    # Create views
    url(r'^vaerktoej/ny$', login_required(CreateTool.as_view()), 
        name='create_tool_v2'),
    url(r'^vaerktoej/flere-nye$', login_required(CreateManyTools.as_view()), 
        name='create_many_tools_v2'),
    url(r'^modeller/ny$', login_required(CreateToolModel.as_view()), 
        name='create_tool_model_v2'),
    url(r'^kategorier/ny$', login_required(CreateToolCategory.as_view()), 
        name='create_tool_category_v2'),
    url(r'^medarbejdere/ny$', login_required(CreateEmployee.as_view()), 
        name='create_employee_v2'),
    url(r'^byggepladser/ny$', login_required(CreateBuildingSite.as_view()), 
        name='create_building_site_v2'),
    url(r'^containere/ny$', login_required(CreateContainer.as_view()),
        name='create_container_v2'),

    # Update views
    url(r'^vaerktoej/(?P<pk>\d+)/rediger/$', 
        login_required(UpdateTool.as_view()), name='update_tool_v2'),
    url(r'^modeller/(?P<pk>\d+)/rediger/$', 
        login_required(UpdateToolModel.as_view()), 
        name='update_tool_model_v2'),
    url(r'^kategorier/(?P<pk>\d+)/rediger/$', 
        login_required(UpdateToolCategory.as_view()), 
        name='update_tool_category_v2'),
    url(r'^medarbejdere/(?P<pk>\d+)/rediger/$', 
        login_required(UpdateEmployee.as_view()), name='update_employee_v2'),
    url(r'^byggepladser/(?P<pk>\d+)/rediger/$', 
        login_required(UpdateBuildingSite.as_view()), 
        name='update_building_site_v2'),
    url(r'^containere/(?P<pk>\d+)/rediger/$', 
        login_required(UpdateContainer.as_view()), name='update_container_v2'),

    # Delete views
    url(r'^vaerktoej/(?P<pk>\d+)/slet/$', login_required(DeleteTool.as_view()),
        name='delete_tool_v2'),
    url(r'^modeller/(?P<pk>\d+)/slet/$', 
        login_required(DeleteToolModel.as_view()),
        name='delete_tool_model_v2'),
    url(r'^kategorier/(?P<pk>\d+)/slet/$', 
        login_required(DeleteToolCategory.as_view()), 
        name='delete_tool_category_v2'),
    url(r'^medarbejdere/(?P<pk>\d+)/slet/$', 
        login_required(DeleteEmployee.as_view()), 
        name='delete_employee_v2'),
    url(r'^byggepladser/(?P<pk>\d+)/slet/$', 
        login_required(DeleteBuildingSite.as_view()), 
        name='delete_building_site_v2'),
    url(r'^containere/(?P<pk>\d+)/slet/$', 
        login_required(DeleteContainer.as_view()), 
        name='delete_container_v2'),
    url(r'^begivenheder/(?P<pk>\d+)/slet/$', 
        login_required(DeleteEvent.as_view()), 
        name='delete_event_v2'),
    url(r'^reservation/(?P<pk>\d+)/slet/$', 
        login_required(DeleteReservation.as_view()), 
        name='delete_reservation_v2'),

    # Action views
    url(r'^vaerktoej/service/$', login_required(ServiceTools.as_view()), 
        name='service_tools_v2'),
    url(r'^vaerktoej/qr-koder/$', login_required(QRTools.as_view()), 
        name='qr_tools_v2'),
    url(r'^vaerktoej/udlaan/$', login_required(LoanTools.as_view()), 
        name='loan_tools_v2'),
    url(r'^vaerktoej/udlaan-enkelt/$', 
        login_required(LoanToolsSingle.as_view()), 
        name='loan_tools_single_v2'),
    url(r'^vaerktoej/reparation/$', login_required(RepairTools.as_view()), 
        name='repair_tools_v2'),
    url(r'^vaerktoej/returnering/$', login_required(ReturnTools.as_view()), 
        name='return_tools_v2'),
    url(r'^vaerktoej/reservation/$', login_required(ReserveTools.as_view()), 
        name='reserve_tools_v2'),
    url(r'^vaerktoej/reservation-enkelt/$', 
        login_required(ReserveToolsSingle.as_view()), 
        name='reserve_tools_single_v2'),
    url(r'^vaerktoej/bortkommet/$', login_required(LostTools.as_view()), 
        name='lost_tools_v2'),
    url(r'^vaerktoej/kasseret/$', login_required(ScrapTools.as_view()), 
        name='scrap_tools_v2'),
    url(r'^vaerktoej/slet/$', login_required(DeleteTools.as_view()), 
        name='delete_tools_v2'),
    url(r'^modeller/slet/$', login_required(DeleteToolModels.as_view()), 
        name='delete_tool_models_v2'),
    url(r'^kategorier/slet/$', login_required(DeleteToolCategories.as_view()), 
        name='delete_tool_categories_v2'),
    url(r'^medarbejdere/aktiv/$', 
        login_required(MakeEmployeesActive.as_view()), 
        name='make_employees_active_v2'),
    url(r'^medarbejdere/inaktiv/$', 
        login_required(MakeEmployeesInactive.as_view()), 
        name='make_employees_inactive_v2'),
    url(r'^medarbejdere/administrator/$', 
        login_required(MakeEmployeesAdmin.as_view()), 
        name='make_employees_admin_v2'),
    url(r'^medarbejdere/fjern-administrator/$', login_required(
        MakeEmployeesNonadmin.as_view()),
        name='make_employees_nonadmin_v2'),
    url(r'^medarbejdere/laaneflag/$', 
        login_required(MakeEmployeesLoanFlagged.as_view()), 
        name='make_employees_loan_flagged_v2'),
    url(r'^medarbejdere/fjern-laaneflag/$', login_required(
        MakeEmployeesNotLoanFlagged.as_view()),
        name='make_employees_not_loan_flagged_v2'),
    url(r'^medarbejdere/slet/$', login_required(DeleteEmployees.as_view()),
        name='delete_employees_v2'),
    url(r'^byggepladser/aktiv/$', 
        login_required(MakeBuildingSitesActive.as_view()), 
        name='make_building_sites_active_v2'),
    url(r'^byggepladser/inaktiv/$', 
        login_required(MakeBuildingSitesInactive.as_view()), 
        name='make_building_sites_inactive_v2'),
    url(r'^byggepladser/slet/$', login_required(DeleteBuildingSites.as_view()),
        name='delete_building_sites_v2'),
    url(r'^containere/aktiv/$', 
        login_required(MakeContainersActive.as_view()), 
        name='make_containers_active_v2'),
    url(r'^containere/inaktiv/$', 
        login_required(MakeContainersInactive.as_view()), 
        name='make_containers_inactive_v2'),
    url(r'^containere/slet/$', login_required(DeleteContainers.as_view()),
        name='delete_containers_v2'),
    url(r'^containere/udlaan/$', login_required(LoanContainers.as_view()), 
        name='loan_containers_v2'),
    url(r'^containere/returnering/$', 
        login_required(ReturnContainers.as_view()), 
        name='return_containers_v2'),

    # Detail views
    url(r'^vaerktoej/(?P<pk>\d+)/$', login_required(ToolDetails.as_view()), 
        name='tool_details_v2'),    
    url(r'^modeller/(?P<pk>\d+)/$', login_required(ToolModelDetails.as_view()),
        name='tool_model_details_v2'),    
    url(r'^kategorier/(?P<pk>\d+)/$', 
        login_required(ToolCategoryDetails.as_view()), 
        name='tool_category_details_v2'),    
    url(r'^medarbejdere/(?P<pk>\d+)/$', 
        login_required(EmployeeDetails.as_view()), 
        name='employee_details_v2'),    
    url(r'^byggepladser/(?P<pk>\d+)/$', 
        login_required(BuildingSiteDetails.as_view()), 
        name='building_site_details_v2'),    
    url(r'^containere/(?P<pk>\d+)/$', 
        login_required(ContainerDetails.as_view()), 
        name='container_details_v2'),    

    # QR views
    url(r'^vaerktoej/(?P<pk>\d+)/qr/$', 'qr_code', name='qr_code_v2'),
    url(r'^vaerktoej/(?P<pk>\d+)/qr-aktion/$', 
        login_required(QRAction.as_view()), name='qr_action_v2'),
    url(r'^qr-succes/$', login_required(QRSuccess.as_view()), 
        name='qr_success_v2'),
)

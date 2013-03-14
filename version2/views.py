# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
import qrcode

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core import serializers
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q, Sum, Avg
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView, DetailView, FormView
from django.views.generic import ListView, RedirectView, TemplateView
from django.views.generic import UpdateView

from tools.models import ConstructionSite, Container, Employee, Event
from tools.models import Login, Reservation, Tool, ToolCategory, ToolModel

from version2.forms import ActionForm, BuildingSiteForm, ContainerForm
from version2.forms import CreateManyToolsForm, DeleteBuildingSitesForm
from version2.forms import DeleteContainersForm, DeleteEmployeesForm
from version2.forms import DeleteToolsForm, DeleteToolCategoriesForm
from version2.forms import DeleteToolModelsForm, EmployeeForm
from version2.forms import LoanContainersForm, LoanToolsForm
from version2.forms import LoanToolsSingleForm, ReserveForm, SettingsForm
from version2.forms import ToolForm, ToolCategoryForm, ToolModelForm
from version2.forms import ReserveToolsSingleForm, ReturnToolsForm

class AjaxResponseMixin(object):
    def get_template_names(self):
        names = super(AjaxResponseMixin, self).get_template_names()

        if self.request.is_ajax():
            names = ['ajax/' + name for name in names]

        return names

class AdminRequired(object):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_admin:
            messages.error(request, 'Du har ikke rettigheder til at se siden')
            return HttpResponseRedirect(reverse('index_v2'))

        return super(AdminRequired, self).dispatch(request, *args, **kwargs)

class ActionView(FormView):
    model = None
    action_function_name = None
    form_class = ActionForm

    def get_initial(self):
        initial = super(ActionView, self).get_initial()
        initial['objects'] = self.request.GET.get('object_ids')
        return initial

    def get_context_data(self, **kwargs):
        context = super(ActionView, self).get_context_data(**kwargs)
        context['objects'] = []

        if self.request.GET.get('object_ids'):
            for object_id in self.request.GET.get('object_ids').split(','):
                obj = get_object_or_404(self.model, pk=object_id)
                context['objects'].append(obj)

        return context

    def get_template_names(self):
        names = super(ActionView, self).get_template_names()
        names = ['actions/' + name for name in names]    
        return names

    def form_valid(self, form):
        message = form.save(self.request.user, self.action_function_name, 
                            self.model)

        if message is not None:
            messages.info(self.request, message)

        return super(ActionView, self).form_valid(form)

class ActionFilterCustomerView(FormView):
    model = None

    def get_initial(self):
        initial = super(ActionFilterCustomerView, self).get_initial()
        initial['objects'] = self.request.GET.get('object_ids')
        return initial

    def get_context_data(self, **kwargs):
        context = super(ActionFilterCustomerView, self).get_context_data(**kwargs)
        context['objects'] = []

        if self.request.GET.get('object_ids'):
            for object_id in self.request.GET.get('object_ids').split(','):
                obj = get_object_or_404(self.model, pk=object_id)
                context['objects'].append(obj)

        return context

    def get_template_names(self):
        names = super(ActionFilterCustomerView, self).get_template_names()
        names = ['actions/' + name for name in names]    
        return names

    def form_valid(self, form):
        message = form.save(self.request.user)

        if message is not None:
            messages.info(self.request, message)

        return super(ActionFilterCustomerView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ActionFilterCustomerView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class JSONResponseMixin(object):
    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('response'):
            response = {'object': serializers.serialize('json', 
                                                        [self.object,])}
            return HttpResponse(json.dumps(response), 
                                content_type='application/json')
        return super(JSONResponseMixin, self).render_to_response(context, **response_kwargs) 

class ToolList(AjaxResponseMixin, ListView):
    model = Tool
    template_name = 'version2/tool_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search')
        order_by = self.request.GET.get('order_by', 'name')

        if search:
            messages.info(self.request, 'Viser søgeresultater for %s' % search)
            return Tool.objects.filter(Q(name__icontains=search) |
                                       Q(model__name__icontains=search) |
                                       Q(model__category__name__icontains=search) |
                                       Q(employee__name__icontains=search) | 
                                       Q(construction_site__name__icontains=search) | 
                                       Q(location__iexact=search) |
                                       Q(secondary_name__icontains=search) |
                                       Q(invoice_number__icontains=search),
                                       model__category__customer=self.request.user.customer).select_related('loaned_to').order_by(order_by)
        else:
            return Tool.objects.filter(model__category__customer=self.request.user.customer).order_by(order_by)

class ToolModelList(AdminRequired, AjaxResponseMixin, ListView):
    model = ToolModel
    template_name = 'version2/tool_model_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search')
        order_by = self.request.GET.get('order_by', 'name')

        if search:
            messages.info(self.request, 'Viser søgeresultater for %s' % search)
            return ToolModel.objects.filter(Q(name__icontains=search) |
                                            Q(category__name__icontains=search),
                                            category__customer=self.request.user.customer).order_by(order_by)
        else:
            return ToolModel.objects.filter(category__customer=self.request.user.customer).order_by(order_by)

class ToolCategoryList(AdminRequired, AjaxResponseMixin, ListView):
    model = ToolCategory
    template_name = 'version2/tool_category_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        order_by = self.request.GET.get('order_by', 'name')

        if search:
            messages.info(self.request, 'Viser søgeresultater for %s' % search)
            return ToolCategory.objects.filter(customer=self.request.user.customer,
                                           name__icontains=search).order_by(order_by)
        else:
            return ToolCategory.objects.filter(customer=self.request.user.customer).order_by(order_by)

class EmployeeList(AdminRequired, AjaxResponseMixin, ListView):
    model = Employee
    template_name = 'version2/employee_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search')
        order_by = self.request.GET.get('order_by', 'name')

        if search:
            messages.info(self.request, 'Viser søgeresultater for %s' % search)
            if search == 'aktiv' or search == 'inaktive':
                return Employee.objects.filter(customer=self.request.user.customer,
                                               is_active=True).order_by(order_by)
            elif search == 'inaktiv' or search == 'inaktive':
                return Employee.objects.filter(customer=self.request.user.customer,
                                               is_active=False).order_by(order_by)
            else:
                return Employee.objects.filter(Q(name__icontains=search) |
                                               Q(phone_number__icontains=search) |
                                               Q(email__icontains=search),
                                               customer=self.request.user.customer).order_by(order_by)
        else:
            return Employee.objects.filter(customer=self.request.user.customer).order_by(order_by)

class BuildingSiteList(AdminRequired, AjaxResponseMixin, ListView):
    model = ConstructionSite
    template_name = 'version2/building_site_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search')
        order_by = self.request.GET.get('order_by', 'name')

        if search:
            if search == 'aktiv' or search == 'aktive':
                return ConstructionSite.objects.filter(customer=self.request.user.customer,
                                                       is_active=True).order_by(order_by)
            elif search == 'inaktiv' or search == 'inaktive':
                return ConstructionSite.objects.filter(customer=self.request.user.customer,
                                                       is_active=False).order_by(order_by)
            else:
                return ConstructionSite.objects.filter(customer=self.request.user.customer,
                                                       name__icontains=search).order_by(order_by)
        else:
            return ConstructionSite.objects.filter(customer=self.request.user.customer).order_by(order_by)

class ContainerList(AdminRequired, AjaxResponseMixin, ListView):
    model = Container
    template_name = 'version2/container_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search')
        order_by = self.request.GET.get('order_by', 'name')

        if search:
            messages.info(self.request, 'Viser søgeresultater for %s' % search)
            return Container.objects.filter(Q(name__icontains=search) |
                                            Q(location__name__icontains=search),
                                            customer=self.request.user.customer).select_related('location').order_by(order_by)
        else:
            return Container.objects.filter(customer=self.request.user.customer).order_by(order_by)

class CreateTool(AdminRequired, CreateView):
    model = Tool
    form_class = ToolForm
    template_name = 'version2/create_tool.html'
    success_url = reverse_lazy('tool_list_v2')

    def form_valid(self, form):
        self.object = form.save()
        event = Event(event_type = "Oprettelse", tool = self.object)
        event.save()

        messages.success(self.request, 'Værktøj oprettet')
        return HttpResponseRedirect(self.get_success_url())

class CreateToolModel(AdminRequired, CreateView):
    model = ToolModel
    form_class = ToolModelForm
    template_name = 'version2/create_tool_model.html'
    success_url = reverse_lazy('tool_model_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Model oprettet')
        return super(CreateToolModel, self).form_valid(form)

class CreateToolCategory(AdminRequired, CreateView):
    model = ToolCategory
    form_class = ToolCategoryForm
    template_name = 'version2/create_tool_category.html'
    success_url = reverse_lazy('tool_category_list_v2')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.customer = self.request.user.customer
        self.object.save()
        messages.success(self.request, 'Kategori oprettet')
        return super(CreateToolCategory, self).form_valid(form)

class CreateEmployee(AdminRequired, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'version2/create_employee.html'
    success_url = reverse_lazy('employee_list_v2')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.customer = self.request.user.customer
        password = Employee.objects.make_random_password()
        self.object.set_password(password)
        self.object.save()

        message = ('Hej ' + self.object.name + '\n' +
                   'Du er netop blevet oprettet i ToolControl-systemet ' +
                   'hos ' + self.object.customer.name + '. Du kan logge ind' +
                   ' med navnet ' + self.object.name + ' samt kodeordet ' + 
                   password + '.' + 
                   '\nMVH\nToolControl')

        self.object.send_message('Oprettet som bruger', message)


        messages.success(self.request, 'Medarbejder oprettet')
        return super(CreateEmployee, self).form_valid(form)

class CreateBuildingSite(AdminRequired, CreateView):
    model = ConstructionSite
    form_class = BuildingSiteForm
    template_name = 'version2/create_building_site.html'
    success_url = reverse_lazy('building_site_list_v2')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.customer = self.request.user.customer
        self.object.save()
        messages.success(self.request, 'Byggeplads oprettet')
        return super(CreateBuildingSite, self).form_valid(form)

class CreateContainer(AdminRequired, CreateView):
    model = Container
    form_class = ContainerForm
    template_name = 'version2/create_container.html'
    success_url = reverse_lazy('container_list_v2')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.customer = self.request.user.customer
        self.object.save()
        messages.success(self.request, 'Container oprettet')
        return super(CreateContainer, self).form_valid(form)

class CreateManyTools(AdminRequired, FormView):
    form_class = CreateManyToolsForm
    template_name = 'version2/create_many_tools.html'
    success_url = reverse_lazy('tool_list_v2')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Værktøj oprettet')
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(CreateManyTools, self).get_form_kwargs()
        kwargs['customer'] = self.request.user.customer
        return kwargs

class UpdateTool(AdminRequired, UpdateView):
    model = Tool
    form_class = ToolForm
    template_name = 'version2/update_tool.html'
    success_url = reverse_lazy('tool_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Værktøj redigeret')
        return super(UpdateTool, self).form_valid(form)

class UpdateToolModel(AdminRequired, UpdateView):
    model = ToolModel
    form_class = ToolModelForm
    template_name = 'version2/update_tool_model.html'
    success_url = reverse_lazy('tool_model_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Model redigeret')
        return super(UpdateToolModel, self).form_valid(form)

class UpdateToolCategory(AdminRequired, UpdateView):
    model = ToolCategory
    form_class = ToolCategoryForm
    template_name = 'version2/update_tool_category.html'
    success_url = reverse_lazy('tool_category_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Kategori redigeret')
        return super(UpdateToolCategory, self).form_valid(form)

class UpdateEmployee(AdminRequired, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'version2/update_employee.html'
    success_url = reverse_lazy('employee_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Medarbejder redigeret')
        return super(UpdateEmployee, self).form_valid(form)

class UpdateBuildingSite(AdminRequired, UpdateView):
    model = ConstructionSite
    form_class = BuildingSiteForm
    template_name = 'version2/update_building_site.html'
    success_url = reverse_lazy('building_site_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Byggeplads redigeret')
        return super(UpdateBuildingSite, self).form_valid(form)

class UpdateContainer(AdminRequired, UpdateView):
    model = Container
    form_class = ContainerForm
    template_name = 'version2/update_container.html'
    success_url = reverse_lazy('container_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Container redigeret')
        return super(UpdateContainer, self).form_valid(form)

class DeleteTool(AdminRequired, DeleteView):
    model = Tool
    template_name = 'version2/tool_confirm_delete.html'
    success_url = reverse_lazy('tool_list_v2')

    def delete(self, request, *args, **kwargs):
        messages.error(request, 'Værktøj slettet')
        return super(DeleteTool, self).delete(request, *args, **kwargs)

class DeleteToolModel(AdminRequired, DeleteView):
    model = ToolModel
    template_name = 'version2/tool_model_confirm_delete.html'
    success_url = reverse_lazy('tool_model_list_v2')

class DeleteToolCategory(AdminRequired, DeleteView):
    model = ToolCategory
    template_name = 'version2/tool_category_confirm_delete.html'
    success_url = reverse_lazy('tool_category_list_v2')

class DeleteEmployee(AdminRequired, DeleteView):
    model = Employee
    template_name = 'version2/employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list_v2')

class DeleteBuildingSite(AdminRequired, DeleteView):
    model = ConstructionSite
    template_name = 'version2/building_site_confirm_delete.html'
    success_url = reverse_lazy('building_site_list_v2')

class DeleteContainer(AdminRequired, DeleteView):
    model = Container
    template_name = 'version2/container_confirm_delete.html'
    success_url = reverse_lazy('container_list_v2')

class DeleteEvent(AdminRequired, DeleteView):
    model = Event
    template_name = 'version2/event_confirm_delete.html'
    success_url = reverse_lazy('tool_list_v2')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.event_type != 'Oprettelse':
            print self.object.event_type
            if (self.object.event_type == 'Kasseret' or
                self.object.event_type == 'Bortkommet'):
                self.object.tool.end_date = None
                self.object.tool.save()

            self.object.delete()
                
        return HttpResponseRedirect(self.get_success_url())

class DeleteReservation(AdminRequired, DeleteView):
    model = Reservation
    template_name = 'version2/reservation_confirm_delete.html'
    success_url = reverse_lazy('tool_list_v2')

class ServiceTools(AdminRequired, ActionView):
    action_function_name = 'service'
    template_name = 'version2/service.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class QRTools(AdminRequired, TemplateView):
    template_name = 'actions/version2/qr_tools.html'

    def get_context_data(self, **kwargs):
        context = super(QRTools, self).get_context_data(**kwargs)
        tools = []

        if self.request.GET.get('object_ids'):
            for tool_id in self.request.GET.get('object_ids').split(','):
                tool = get_object_or_404(Tool, pk=tool_id)
                tools.append(tool)

        context['tools'] = tools
        return context

class LoanTools(AdminRequired, ActionFilterCustomerView):
    form_class = LoanToolsForm
    template_name = 'version2/loan.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class RepairTools(AdminRequired, ActionView):
    action_function_name = 'repair'
    template_name = 'version2/repair.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class LoanToolsSingle(ActionView):
    action_function_name = 'loan'
    template_name = 'version2/loan_single.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class ReserveToolsSingle(FormView):
    form_class = ReserveToolsSingleForm
    template_name = 'actions/version2/reserve_single.html'
    success_url = reverse_lazy('tool_list_v2')

    def form_valid(self, form):
        message = form.save(self.request.user)

        if message is not None:
            messages.info(self.request, message)

        return super(ReserveToolsSingle, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ReserveToolsSingle, self).get_context_data(**kwargs)
        context['objects'] = []

        if self.request.GET.get('object_ids'):
            for object_id in self.request.GET.get('object_ids').split(','):
                obj = get_object_or_404(Tool, pk=object_id)
                context['objects'].append(obj)

        return context

    def get_initial(self):
        initial = super(ReserveToolsSingle, self).get_initial()
        initial['objects'] = self.request.GET.get('object_ids')
        return initial

class ReturnTools(ActionView):
    action_function_name = 'end_loan'
    template_name = 'version2/return.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class ReserveTools(ActionFilterCustomerView):
    form_class = ReserveForm
    template_name = 'version2/reserve.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class ScrapTools(AdminRequired, ActionView):
    action_function_name = 'scrap'
    template_name = 'version2/scrap.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class LostTools(AdminRequired, ActionView):
    action_function_name = 'lost'
    template_name = 'version2/lost.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class DeleteTools(AdminRequired, ActionView):
    action_function_name = 'delete'
    template_name = 'version2/delete_tools.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class DeleteToolModels(AdminRequired, ActionView):
    action_function_name = 'delete'
    template_name = 'version2/delete_models.html'
    success_url = reverse_lazy('tool_model_list_v2')
    model = ToolModel

class DeleteToolCategories(AdminRequired, ActionView):
    action_function_name = 'delete'
    template_name = 'version2/delete_tool_categories.html'
    success_url = reverse_lazy('tool_category_list_v2')
    model = ToolCategory

class MakeEmployeesActive(AdminRequired, ActionView):
    action_function_name = 'make_active'
    template_name = 'version2/make_employees_active.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeEmployeesInactive(AdminRequired, ActionView):
    action_function_name = 'make_inactive'
    template_name = 'version2/make_employees_inactive.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeEmployeesAdmin(AdminRequired, ActionView):
    action_function_name = 'make_admin'
    template_name = 'version2/make_employees_admin.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeEmployeesNonadmin(AdminRequired, ActionView):
    action_function_name = 'make_not_admin'
    template_name = 'version2/make_employees_nonadmin.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeEmployeesLoanFlagged(AdminRequired, ActionView):
    action_function_name = 'make_loan_flagged'
    template_name = 'version2/make_employees_loan_flagged.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeEmployeesNotLoanFlagged(AdminRequired, ActionView):
    action_function_name = 'make_not_loan_flagged'
    template_name = 'version2/make_employees_not_loan_flagged.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class DeleteEmployees(AdminRequired, ActionView):
    action_function_name = 'delete'
    template_name = 'version2/delete_employees.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeBuildingSitesActive(AdminRequired, ActionView):
    action_function_name = 'make_active'
    template_name = 'version2/make_building_sites_active.html'
    success_url = reverse_lazy('building_site_list_v2')
    model = ConstructionSite

class MakeBuildingSitesInactive(AdminRequired, ActionView):
    action_function_name = 'make_inactive'
    template_name = 'version2/make_building_sites_inactive.html'
    success_url = reverse_lazy('building_site_list_v2')
    model = ConstructionSite

class DeleteBuildingSites(AdminRequired, ActionView):
    action_function_name = 'delete'
    template_name = 'version2/delete_building_sites.html'
    success_url = reverse_lazy('building_site_list_v2')
    model = ConstructionSite

class MakeContainersActive(AdminRequired, ActionView):
    action_function_name = 'make_active'
    template_name = 'version2/make_containers_active.html'
    success_url = reverse_lazy('container_list_v2')
    model = Container

class MakeContainersInactive(AdminRequired, ActionView):
    action_function_name = 'make_inactive'
    template_name = 'version2/make_containers_inactive.html'
    success_url = reverse_lazy('container_list_v2')
    model = Container

class DeleteContainers(AdminRequired, ActionView):
    action_function_name = 'delete'
    template_name = 'version2/delete_containers.html'
    success_url = reverse_lazy('container_list_v2')
    model = Container

class LoanContainers(AdminRequired, ActionFilterCustomerView):
    form_class = LoanContainersForm
    template_name = 'version2/loan_containers.html'
    success_url = reverse_lazy('container_list_v2')
    model = Container

class ReturnContainers(AdminRequired, ActionView):
    action_function_name = 'end_loan'
    template_name = 'version2/return_containers.html'
    success_url = reverse_lazy('container_list_v2')
    model = Container

class ToolDetails(DetailView):
    model = Tool
    template_name = 'version2/tool_details.html'

class ToolModelDetails(AdminRequired, JSONResponseMixin, DetailView):
    model = ToolModel
    template_name = 'version2/tool_model_details.html'

class ToolCategoryDetails(AdminRequired, DetailView):
    model = ToolCategory
    template_name = 'version2/tool_category_details.html'

class EmployeeDetails(AdminRequired, DetailView):
    model = Employee
    template_name = 'version2/employee_details.html'

class BuildingSiteDetails(AdminRequired, DetailView):
    model = ConstructionSite
    template_name = 'version2/building_site_details.html'

class ContainerDetails(AdminRequired, DetailView):
    model = Container
    template_name = 'version2/container_details.html'

class Settings(UpdateView):
    form_class = SettingsForm
    template_name = 'version2/settings.html'
    model = Employee

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, 'Indstillinger opdateret')
        return reverse_lazy('settings_v2')

class ChangePassword(FormView):
    form_class = PasswordChangeForm
    template_name = 'version2/change_password.html'

    def get_form_kwargs(self):
        kwargs = super(ChangePassword, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        messages.success(self.request, 'Kodeord ændret')
        return reverse_lazy('change_password_v2')

class Stats(AdminRequired, TemplateView):
    template_name = 'version2/stats.html'

    def get_context_data(self, **kwargs):
        context = super(Stats, self).get_context_data(**kwargs)

        lost_tool_count = Tool.objects.filter(location='Bortkommet', model__category__customer=self.request.user.customer).count()
        scrapped_tool_count = Tool.objects.filter(location='Kasseret', model__category__customer=self.request.user.customer).count()
        
        try:
            lost_tools_ratio = (lost_tool_count / (float(scrapped_tool_count + lost_tool_count)) * 100)
            scrapped_tools_ratio = (scrapped_tool_count / (float(scrapped_tool_count + lost_tool_count)) * 100)
        except ZeroDivisionError:
            scrapped_tools_ratio = 0
            lost_tools_ratio = 0

        alive_tools = Tool.objects.filter(end_date__isnull=True, model__category__customer=self.request.user.customer)
        timedeltas = [datetime.date.today() - tool.buy_date for tool in alive_tools]
        try:
            average_age = (sum(timedeltas, datetime.timedelta(0)) / alive_tools.count()).days
        except ZeroDivisionError:
            average_age = 0

        dead_tools = Tool.objects.filter(end_date__isnull=False, model__category__customer=self.request.user.customer)
        timedeltas = [tool.end_date - tool.buy_date for tool in dead_tools]
        try:
            average_life = (sum(timedeltas, datetime.timedelta(0)) / dead_tools.count()).days
        except ZeroDivisionError:
            average_life = 0

        context['tool_count'] = Tool.objects.filter(model__category__customer=self.request.user.customer).count()
        context['model_count'] = ToolModel.objects.filter(category__customer=self.request.user.customer).count()
        context['category_count'] = ToolCategory.objects.filter(customer=self.request.user.customer).count()
        context['sum_price_tools'] = Tool.objects.filter(model__category__customer=self.request.user.customer).aggregate(Sum('price'))
        context['avg_price_tools'] = Tool.objects.filter(model__category__customer=self.request.user.customer).aggregate(Avg('price'))
        context['avg_price_models'] = ToolModel.objects.filter(category__customer=self.request.user.customer).aggregate(Avg('price'))
        context['lost_tool_count'] = lost_tool_count
        context['scrapped_tool_count'] = scrapped_tool_count
        context['scrapped_tools_ratio'] = scrapped_tools_ratio
        context['lost_tools_ratio'] = lost_tools_ratio
        context['average_age'] = average_age
        context['average_life'] = average_life

        return context

class EmployeeStats(AdminRequired, ListView):
    model = Employee
    template_name = 'version2/employee_stats.html'

def qr_code(request, pk):
    if not request.user.customer:
        return HttpResponseRedirect(reverse('admin_index'))

    path = reverse('qr_action_v2', args=[pk])
    img = qrcode.make('http://toolcontrol.dk/' + path)
    response = HttpResponse(mimetype='image/png')
    img.save(response, 'PNG')
    return response

class QRAction(FormView):
    form_class = LoanToolsForm
    template_name = 'version2/qr_action.html'
    success_url = reverse_lazy('qr_success_v2')

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Tool, pk = kwargs['pk'])

        if self.object.location == 'Udlånt':
            self.form_class = ReturnToolsForm
        elif not request.user.is_admin:
            self.form_class = LoanToolsSingleForm

        return super(QRAction, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QRAction, self).get_context_data(**kwargs)
        context['tool'] = self.object
        return context

    def get_initial(self):
        initial = super(QRAction, self).get_initial()
        initial['objects'] = self.object.pk
        return initial

    def get_form_kwargs(self):
        kwargs = super(QRAction, self).get_form_kwargs()

        if self.form_class == LoanToolsForm:
            kwargs['user'] = self.request.user
        
        return kwargs

    def form_valid(self, form):
        response = form.save(self.request.user)
        messages.info(self.request, response)
        return super(QRAction, self).form_valid(form)

class QRSuccess(TemplateView):
    template_name = 'version2/qr_success.html'

class LoginView(FormView):
    form_class = AuthenticationForm
    success_url = reverse_lazy('index_v2')
    template_name = 'version2/login.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        l = Login(employee = user)
        l.save()
        return super(LoginView, self).form_valid(form)

class LogoutView(RedirectView):
    url = reverse_lazy('login_v2')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)

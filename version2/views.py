# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView, DetailView, FormView
from django.views.generic import ListView, UpdateView

from tools.models import ConstructionSite, Container, Employee
from tools.models import Tool, ToolCategory, ToolModel

from version2.forms import BuildingSiteForm, ContainerForm, EmployeeForm
from version2.forms import ToolForm, ToolCategoryForm, ToolModelForm
from version2.forms import LoanForm, RepairForm, ReturnForm, ServiceForm
from version2.forms import ReserveForm, ScrapForm, LostForm, DeleteToolsForm
from version2.forms import DeleteToolModelsForm, DeleteToolCategoriesForm
from version2.forms import MakeEmployeesActiveForm, MakeEmployeesInactiveForm
from version2.forms import MakeEmployeesAdminForm, MakeEmployeesNonadminForm
from version2.forms import MakeEmployeesLoanFlaggedForm, DeleteEmployeesForm
from version2.forms import MakeEmployeesNotLoanFlaggedForm
from version2.forms import MakeBuildingSitesActiveForm, DeleteBuildingSitesForm
from version2.forms import MakeBuildingSitesInactiveForm
from version2.forms import MakeContainersActiveForm, DeleteContainersForm
from version2.forms import MakeContainersInactiveForm

class AjaxResponseMixin(object):
    def get_template_names(self):
        names = super(AjaxResponseMixin, self).get_template_names()

        if self.request.is_ajax():
            names = ['ajax/' + name for name in names]

        return names

class ActionView(FormView):
    model = None

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
        form.save(self.request.user)
        return super(ActionView, self).form_valid(form)

class ToolList(AjaxResponseMixin, ListView):
    model = Tool
    template_name = 'version2/tool_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search')

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
                                       model__category__customer=self.request.user.customer).select_related('loaned_to')
        else:
            return Tool.objects.all()

class ToolModelList(AjaxResponseMixin, ListView):
    model = ToolModel
    template_name = 'version2/tool_model_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search')

        if search:
            messages.info(self.request, 'Viser søgeresultater for %s' % search)
            return ToolModel.objects.filter(Q(name__icontains=search) |
                                            Q(category__name__icontains=search),
                                            category__customer=self.request.user.customer)
        else:
            return ToolModel.objects.all()

class ToolCategoryList(AjaxResponseMixin, ListView):
    model = ToolCategory
    template_name = 'version2/tool_category_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search', '')

        if search:
            messages.info(self.request, 'Viser søgeresultater for %s' % search)
            return ToolCategory.objects.filter(customer=self.request.user.customer,
                                           name__icontains=search)
        else:
            return ToolCategory.objects.all()

class EmployeeList(AjaxResponseMixin, ListView):
    model = Employee
    template_name = 'version2/employee_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search')

        if search:
            messages.info(self.request, 'Viser søgeresultater for %s' % search)
            if search == 'aktiv' or search == 'inaktive':
                return Employee.objects.filter(customer=self.request.user.customer,
                                               is_active=True)
            elif search == 'inaktiv' or search == 'inaktive':
                return Employee.objects.filter(customer=self.request.user.customer,
                                               is_active=False)
            else:
                return Employee.objects.filter(Q(name__icontains=search) |
                                               Q(phone_number__icontains=search) |
                                               Q(email__icontains=search),
                                               customer=self.request.user.customer)
        else:
            return Employee.objects.all()

class BuildingSiteList(AjaxResponseMixin, ListView):
    model = ConstructionSite
    template_name = 'version2/building_site_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search')

        if search:
            if search == 'aktiv' or search == 'aktive':
                return ConstructionSite.objects.filter(customer=self.request.user.customer,
                                                       is_active=True)
            elif search == 'inaktiv' or search == 'inaktive':
                return ConstructionSite.objects.filter(customer=self.request.user.customer,
                                                       is_active=False)
            else:
                return ConstructionSite.objects.filter(customer=self.request.user.customer,
                                                       name__icontains=search)
        else:
            return ConstructionSite.objects.all()

class ContainerList(AjaxResponseMixin, ListView):
    model = Container
    template_name = 'version2/container_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search')

        if search:
            messages.info(self.request, 'Viser søgeresultater for %s' % search)
            return Container.objects.filter(Q(name__icontains=search) |
                                            Q(location__name__icontains=search),
                                            customer=self.request.user.customer).select_related('location')
        else:
            return Container.objects.all()

class CreateTool(CreateView):
    model = Tool
    form_class = ToolForm
    template_name = 'version2/create_tool.html'
    success_url = reverse_lazy('tool_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Værktøj oprettet')
        return super(CreateTool, self).form_valid(form)

class CreateToolModel(CreateView):
    model = ToolModel
    form_class = ToolModelForm
    template_name = 'version2/create_tool_model.html'
    success_url = reverse_lazy('tool_model_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Model oprettet')
        return super(CreateToolModel, self).form_valid(form)

class CreateToolCategory(CreateView):
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

class CreateEmployee(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'version2/create_employee.html'
    success_url = reverse_lazy('employee_list_v2')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.customer = self.request.user.customer
        self.object.set_password(Employee.objects.make_random_password())
        self.object.save()
        messages.success(self.request, 'Medarbejder oprettet')
        return super(CreateEmployee, self).form_valid(form)

class CreateBuildingSite(CreateView):
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

class CreateContainer(CreateView):
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

class UpdateTool(UpdateView):
    model = Tool
    form_class = ToolForm
    template_name = 'version2/update_tool.html'
    success_url = reverse_lazy('tool_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Værktøj redigeret')
        return super(UpdateTool, self).form_valid(form)

class UpdateToolModel(UpdateView):
    model = ToolModel
    form_class = ToolModelForm
    template_name = 'version2/update_tool_model.html'
    success_url = reverse_lazy('tool_model_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Model redigeret')
        return super(UpdateToolModel, self).form_valid(form)

class UpdateToolCategory(UpdateView):
    model = ToolCategory
    form_class = ToolCategoryForm
    template_name = 'version2/update_tool_category.html'
    success_url = reverse_lazy('tool_category_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Kategori redigeret')
        return super(UpdateToolCategory, self).form_valid(form)

class UpdateEmployee(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'version2/update_employee.html'
    success_url = reverse_lazy('employee_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Medarbejder redigeret')
        return super(UpdateEmployee, self).form_valid(form)

class UpdateBuildingSite(UpdateView):
    model = ConstructionSite
    form_class = BuildingSiteForm
    template_name = 'version2/update_building_site.html'
    success_url = reverse_lazy('building_site_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Byggeplads redigeret')
        return super(UpdateBuildingSite, self).form_valid(form)

class UpdateContainer(UpdateView):
    model = Container
    form_class = ContainerForm
    template_name = 'version2/update_container.html'
    success_url = reverse_lazy('container_list_v2')

    def form_valid(self, form):
        messages.success(self.request, 'Container redigeret')
        return super(UpdateContainer, self).form_valid(form)

class DeleteTool(DeleteView):
    model = Tool
    template_name = 'version2/tool_confirm_delete.html'
    success_url = reverse_lazy('tool_list_v2')

    def delete(self, request, *args, **kwargs):
        messages.error(request, 'Værktøj slettet')
        return super(DeleteTool, self).delete(request, *args, **kwargs)

class DeleteToolModel(DeleteView):
    model = ToolModel
    template_name = 'version2/tool_model_confirm_delete.html'
    success_url = reverse_lazy('tool_model_list_v2')

class DeleteToolCategory(DeleteView):
    model = ToolCategory
    template_name = 'version2/tool_category_confirm_delete.html'
    success_url = reverse_lazy('tool_category_list_v2')

class DeleteEmployee(DeleteView):
    model = Employee
    template_name = 'version2/employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list_v2')

class DeleteBuildingSite(DeleteView):
    model = ConstructionSite
    template_name = 'version2/building_site_confirm_delete.html'
    success_url = reverse_lazy('building_site_list_v2')

class DeleteContainer(DeleteView):
    model = Container
    template_name = 'version2/container_confirm_delete.html'
    success_url = reverse_lazy('container_list_v2')

class ServiceTools(ActionView):
    form_class = ServiceForm
    template_name = 'version2/service.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class LoanTools(ActionView):
    form_class = LoanForm
    template_name = 'version2/loan.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class RepairTools(ActionView):
    form_class = RepairForm
    template_name = 'version2/repair.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class ReturnTools(ActionView):
    form_class = ReturnForm
    template_name = 'version2/return.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class ReserveTools(ActionView):
    form_class = ReserveForm
    template_name = 'version2/reserve.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class ScrapTools(ActionView):
    form_class = ScrapForm
    template_name = 'version2/scrap.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class LostTools(ActionView):
    form_class = LostForm
    template_name = 'version2/lost.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class DeleteTools(ActionView):
    form_class = DeleteToolsForm
    template_name = 'version2/delete_tools.html'
    success_url = reverse_lazy('tool_list_v2')
    model = Tool

class DeleteToolModels(ActionView):
    form_class = DeleteToolModelsForm
    template_name = 'version2/delete_models.html'
    success_url = reverse_lazy('tool_model_list_v2')
    model = ToolModel

class DeleteToolCategories(ActionView):
    form_class = DeleteToolCategoriesForm
    template_name = 'version2/delete_tool_categories.html'
    success_url = reverse_lazy('tool_category_list_v2')
    model = ToolCategory

class MakeEmployeesActive(ActionView):
    form_class = MakeEmployeesActiveForm
    template_name = 'version2/make_employees_active.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeEmployeesInactive(ActionView):
    form_class = MakeEmployeesInactiveForm
    template_name = 'version2/make_employees_inactive.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeEmployeesAdmin(ActionView):
    form_class = MakeEmployeesAdminForm
    template_name = 'version2/make_employees_admin.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeEmployeesNonadmin(ActionView):
    form_class = MakeEmployeesNonadminForm
    template_name = 'version2/make_employees_nonadmin.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeEmployeesLoanFlagged(ActionView):
    form_class = MakeEmployeesLoanFlaggedForm
    template_name = 'version2/make_employees_loan_flagged.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeEmployeesNotLoanFlagged(ActionView):
    form_class = MakeEmployeesNotLoanFlaggedForm
    template_name = 'version2/make_employees_not_loan_flagged.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class DeleteEmployees(ActionView):
    form_class = DeleteEmployeesForm
    template_name = 'version2/delete_employees.html'
    success_url = reverse_lazy('employee_list_v2')
    model = Employee

class MakeBuildingSitesActive(ActionView):
    form_class = MakeBuildingSitesActiveForm
    template_name = 'version2/make_building_sites_active.html'
    success_url = reverse_lazy('building_site_list_v2')
    model = ConstructionSite

class MakeBuildingSitesInactive(ActionView):
    form_class = MakeBuildingSitesInactiveForm
    template_name = 'version2/make_building_sites_inactive.html'
    success_url = reverse_lazy('building_site_list_v2')
    model = ConstructionSite

class DeleteBuildingSites(ActionView):
    form_class = DeleteBuildingSitesForm
    template_name = 'version2/delete_building_sites.html'
    success_url = reverse_lazy('building_site_list_v2')
    model = ConstructionSite

class MakeContainersActive(ActionView):
    form_class = MakeContainersActiveForm
    template_name = 'version2/make_containers_active.html'
    success_url = reverse_lazy('container_list_v2')
    model = Container

class MakeContainersInactive(ActionView):
    form_class = MakeContainersInactiveForm
    template_name = 'version2/make_containers_inactive.html'
    success_url = reverse_lazy('container_list_v2')
    model = Container

class DeleteContainers(ActionView):
    form_class = DeleteContainersForm
    template_name = 'version2/delete_containers.html'
    success_url = reverse_lazy('container_list_v2')
    model = Container


class ToolDetails(DetailView):
    model = Tool
    template_name = 'version2/tool_details.html'

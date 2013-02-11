# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import datetime, logging, qrcode
logger = logging.getLogger(__name__)

from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Avg, Sum, Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import simplejson
from django.views.generic import ListView
from django.views.generic.edit import FormView

from tools.forms import BuildingSiteForm, ContainerForm, ContainerLoanForm
from tools.forms import CreateManyToolsForm, EmployeeForm, ForgotPasswordForm
from tools.forms import LoanForm, QRLoanForm, SettingsForm, ToolForm
from tools.forms import ToolCategoryForm, ToolModelForm

from tools.models import ConstructionSite, Container, Event, Employee, Tool
from tools.models import ForgotPasswordToken, ToolCategory, ToolModel

from toolcontrol.enums import TOOL_FAILURES
from toolcontrol.utils import handle_loan_messages

def login_view(request):
    if request.POST:
        authentication_form = AuthenticationForm(data=request.POST)
        logger.info('%s is trying to log in' % request.POST.get('username'))
        if authentication_form.is_valid():
            user = authentication_form.get_user()
            login(request, user)
            logger.info('Login successful')
            return HttpResponseRedirect(reverse('index'))
    else:
        authentication_form = AuthenticationForm()

    context_dictionary = {'authentication_form': authentication_form}
    return render(request, 'login.html', context_dictionary)

@login_required
def logout_view(request):
    logger.info('%s has logged out' % request.user)
    logout(request)
    return HttpResponseRedirect(reverse('login'))

@login_required
def settings(request):
    password_change_form = PasswordChangeForm(request.user)
    settings_form = SettingsForm(instance=request.user)

    if request.POST:
        form = request.POST.get('form')
        if form == 'password_change':
            logger.info('%s is trying to change password' % request.user)
            password_change_form = PasswordChangeForm(user = request.user,
                                                      data = request.POST)
            if password_change_form.is_valid():
                password_change_form.save()
                logger.info('Password changed succesfully')
                password_change_form = PasswordChangeForm(request.user)
            else:
                logger.info('Password not changed')
        elif form == 'settings':
            logger.info('%s is trying to change settings' % request.user)
            settings_form = SettingsForm(instance = request.user,
                                         data = request.POST)
            if settings_form.is_valid():
                settings_form.save()
                logger.info('Settings changed succesfully')
            else:
                logger.info('Settings not succesfully')

    context_dictionary = {
        'password_change_form': password_change_form,
        'settings_form': settings_form,
        }

    return render(request, 'settings.html', context_dictionary)

@login_required
def stats(request):
    lost_tool_count = Tool.objects.filter(location='Bortkommet').count()
    scrapped_tool_count = Tool.objects.filter(location='Kasseret').count()
    
    try:
        lost_tools_ratio = (lost_tool_count / 
                            (float(scrapped_tool_count + 
                                   lost_tool_count)) * 100)
        scrapped_tools_ratio = (scrapped_tool_count / 
                                (float(scrapped_tool_count + 
                                       lost_tool_count)) * 100)
    except ZeroDivisionError:
        scrapped_tools_ratio = 0
        lost_tools_ratio = 0

    alive_tools = Tool.objects.filter(end_date__isnull=True)
    timedeltas = [datetime.datetime.now() - tool.buy_date for tool in alive_tools]
    try:
        average_age = (sum(timedeltas, datetime.timedelta(0)) / alive_tools.count()).days
    except ZeroDivisionError:
        average_age = 0

    dead_tools = Tool.objects.filter(end_date__isnull=False)
    timedeltas = [tool.end_date - tool.buy_date for tool in dead_tools]
    try:
        average_life = (sum(timedeltas, datetime.timedelta(0)) / dead_tools.count()).days
    except ZeroDivisionError:
        average_life = 0

    context_dictionary = {
        'tool_count': Tool.objects.all().count(),
        'model_count': ToolModel.objects.all().count(),
        'category_count': ToolCategory.objects.all().count(),
        'sum_price_tools': Tool.objects.all().aggregate(Sum('price')),
        'avg_price_tools': Tool.objects.all().aggregate(Avg('price')),
        'avg_price_models': ToolModel.objects.all().aggregate(Avg('price')),
        'lost_tool_count': lost_tool_count,
        'scrapped_tool_count': scrapped_tool_count,
        'scrapped_tools_ratio': scrapped_tools_ratio,
        'lost_tools_ratio': lost_tools_ratio,
        'average_age': average_age,
        'average_life': average_life,
        }

    return render(request, 'stats.html', context_dictionary)

class IndexView(FormView):
    template_name = 'index.html'
    form_class = CreateManyToolsForm
    success_url = '/'

    def form_valid(self, form):
        form.save()
        logger.info('Many tools created successfully')
        return super(IndexView, self).form_valid(form)

    def form_invalid(self, form):
        logger.info('Many tools not created (%s)', form.errors)
        return super(IndexView, self).form_invalid(form)

class ContainerListView(ListView):
    template_name = 'container_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        ordering = self.request.GET.get('ordering', 'name')

        return Container.objects.filter(Q(name__icontains=search) |
                                        Q(location__name__icontains=search)).select_related('location').order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super(ContainerListView, self).get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search')
        context['ordering'] = self.request.GET.get('ordering')
        return context

class ToolListView(ListView):
    template_name = 'tool_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        ordering = self.request.GET.get('ordering', 'name')

        return Tool.objects.filter(Q(name__icontains=search) |
                                   Q(model__name__icontains=search) |
                                   Q(model__category__name__icontains=search) |
                                   Q(employee__name__icontains=search) | 
                                   Q(construction_site__name__icontains=search) | 
                                   Q(location__iexact=search) |
                                   Q(secondary_name__icontains=search) |
                                   Q(invoice_number__icontains=search)).select_related('loaned_to').order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super(ToolListView, self).get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search')
        context['ordering'] = self.request.GET.get('ordering')
        return context

class ModelListView(ListView):
    template_name = 'model_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        ordering = self.request.GET.get('ordering', 'name')

        return ToolModel.objects.filter(Q(name__icontains=search) |
                                        Q(category__name__icontains=search)).order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super(ModelListView, self).get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search')
        context['ordering'] = self.request.GET.get('ordering')
        return context

class CategoryListView(ListView):
    template_name = 'category_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        ordering = self.request.GET.get('ordering', 'name')

        return ToolCategory.objects.filter(name__icontains=search).order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search')
        context['ordering'] = self.request.GET.get('ordering')
        return context

class EmployeeListView(ListView):
    template_name = 'employee_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        ordering = self.request.GET.get('ordering', 'name')

        if search == 'aktiv' or search == 'inaktive':
            return Employee.objects.filter(is_active=True).order_by(sorting)
        elif search == 'inaktiv' or search == 'inaktive':
            return Employee.objects.filter(is_active=False).order_by(sorting)
        else:
            return Employee.objects.filter(Q(name__icontains=search) |
                                           Q(phone_number__icontains=search) |
                                           Q(email__icontains=search)).order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super(EmployeeListView, self).get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search')
        context['ordering'] = self.request.GET.get('ordering')
        return context

class ConstructionSiteListView(ListView):
    template_name = 'building_site_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        ordering = self.request.GET.get('ordering', 'name')

        if search == 'aktiv' or search == 'aktive':
            return ConstructionSite.objects.filter(is_active=True).order_by(sorting)
        elif search == 'inaktiv' or search == 'inaktive':
            return ConstructionSite.objects.filter(is_active=False).order_by(sorting)
        else:
            return ConstructionSite.objects.filter(name__icontains=search).order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super(ConstructionSiteListView, self).get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search')
        context['ordering'] = self.request.GET.get('ordering')
        return context

class EventListView(ListView):
    template_name = 'event_list.html'
    
    def get_queryset(self):
        tool_id = self.request.GET.get('tool_id')
        tool = get_object_or_404(Tool, id = tool_id)

        return Event.objects.filter(tool=tool).order_by('start_date')

class LoanListView(ListView):
    template_name = 'loan_list.html'

    def get_queryset(self):
        loaner_id = self.request.GET.get('loaner_id')
        object_type = self.request.GET.get('object_type')
    
        if object_type == 'employee':
            employee = get_object_or_404(Employee, id = loaner_id)
            return Event.objects.filter(employee=employee).order_by('-start_date')
        elif object_type == 'building_site':
            construction_site = get_object_or_404(ConstructionSite, id = loaner_id)
            return Event.objects.filter(construction_site=construction_site).order_by('-start_date')

class SimpleToolListView(ListView):
    template_name = 'simple_tool_list.html'

    def get_queryset(self):
        show_model = self.request.GET.get('show_model')
        
        if show_model == 'true':
            if self.request.GET.get('category_id'):
                category_id = self.request.GET.get('category_id')
                category = get_object_or_404(ToolCategory, id = category_id)
                return Tool.objects.filter(model__category=category).order_by('name')
            elif self.request.GET.get('container_id'):
                container_id = self.request.GET.get('container_id')
                container = get_object_or_404(Container, id = container_id)
                return Tool.objects.filter(container=container).order_by('name')
        else:
            model_id = self.request.GET.get('model_id')
            model = get_object_or_404(ToolModel, id = model_id)
            return Tool.objects.filter(model=model).order_by('name')

    def get_context_data(self, **kwargs):
        context = super(SimpleToolListView, self).get_context_data(**kwargs)

        show_model = self.request.GET.get('show_model')

        if show_model == 'true':
            context['show_model'] = True
        else:
            context['show_model'] = False

        return context

@login_required
def container_banner(request):
    context = {}
    return render(request, 'container_banner.html', context)

@login_required
def tool_banner(request):
    context = {}
    return render(request, 'tool_banner.html', context)

@login_required
def model_banner(request):
    if not request.user.is_admin():
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'model_banner.html', context)

@login_required
def category_banner(request):
    if not request.user.is_admin():
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'category_banner.html', context)

@login_required
def employee_banner(request):
    if not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'employee_banner.html', context)

@login_required
def building_site_banner(request):
    if not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'building_site_banner.html', context)

@login_required
def container_form(request):
    if request.POST:
        container_id = request.POST.get('id', 0)

        # Edit an existing container
        if container_id != 0:
            container = get_object_or_404(Container, id = container_id)
            logger.info('%s is editing a container (%s)' % (request.user, container.name))
            container_form = ContainerForm(data = request.POST, 
                                           instance = container)
            if container_form.is_valid():
                container_form.save()
                logger.info('container successfully edited')
                response = {'response': 'Container redigeret'}
            else:
                logger.info('container not edited')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        else:
            logger.info('%s is creating a container (%s)' % (request.user, request.POST.get('name')))
            container_form = ContainerForm(request.POST)
            if container_form.is_valid():
                container_form.save()
                logger.info('container successfully created')
                response = {'response': 'Container oprettet'}
            else:
                logger.info('container not created')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")
            
    container_id = request.GET.get('id')

    if container_id:
        container = get_object_or_404(Container, id = container_id)
        container_form = ContainerForm(instance=container)
        context = {'form': container_form,
                   'object_type': 'container',
                   'id': container.id}
    else:
        container_form = ContainerForm()
        context = {'form': container_form,
                   'object_type': 'container'}

    return render(request, 'form.html', context)

@login_required
def tool_form(request):
    if request.POST:
        tool_id = request.POST.get('id', 0)

        # Edit an existing tool
        if tool_id != 0:
            tool = get_object_or_404(Tool, id = tool_id)
            logger.info('%s is editing a tool (%s)' % (request.user, tool.name))
            tool_form = ToolForm(data = request.POST, instance = tool)

            if tool_form.is_valid():
                new_tool = tool_form.save()
                logger.info('Tool edited successfully')
                tool_form = ToolForm()

                response = {'response': 'Værktøj redigeret'}
            else:
                logger.info('Tool not edited')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        # Create new tool
        else:
            logger.info('%s is creating a tool (%s)' % (request.user,
                                                        request.POST.get('name')))
            tool_form = ToolForm(request.POST)
            if tool_form.is_valid():
                tool = tool_form.save()
                logger.info('Tool successfully created')
                event = Event(event_type="Oprettelse", tool=tool)
                event.save()
                
                response = {'response': 'Værktøj oprettet'}
            else:
                logger.info('Tool not created')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    tool_id = request.GET.get('id')

    if tool_id:
        tool = get_object_or_404(Tool, id = tool_id)
        tool_form = ToolForm(instance=tool)
        context = {'form': tool_form,
                   'object_type': 'tool',
                   'id': tool.id}
    else:
        tool_form = ToolForm()
        context = {'form': tool_form,
                   'object_type': 'tool'}

    return render(request, 'form.html', context)

@login_required
def model_form(request):
    if request.POST:
        model_id = request.POST.get('id', 0)

        # Edit an existing model
        if model_id != 0:
            model = get_object_or_404(ToolModel, id = model_id)
            logger.info('%s is editing a model (%s)' % (request.user, model.name))
            model_form = ToolModelForm(data = request.POST, instance = model)

            if model_form.is_valid():
                new_model = model_form.save()
                logger.info('Model successfully edited')
                model_form = ToolModelForm()

                response = {'response': 'Model redigeret'}
            else:
                logger.info('Model not edited')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        else:
            logger.info('%s is creating a model (%s)' % (request.user, request.POST.get('name')))
            model_form = ToolModelForm(request.POST)
            if model_form.is_valid():
                model = model_form.save()
                logger.info('Model successfully created')
                model_form = ToolModelForm()
            
                response = {'response': 'Model oprettet'}
            else:
                logger.info('Model not created')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")


    model_id = request.GET.get('id')

    if model_id:
        model = get_object_or_404(ToolModel, id = model_id)
        model_form = ToolModelForm(instance=model)
        context = {'form': model_form,
                   'object_type': 'model',
                   'id': model.id}
    else:
        model_form = ToolModelForm()
        context = {'form': model_form,
                   'object_type': 'model'}

    return render(request, 'form.html', context)

@login_required
def category_form(request):
    if request.POST:
        category_id = request.POST.get('id', 0)

        # Edit an existing category
        if category_id != 0:
            category = get_object_or_404(ToolCategory, id = category_id)
            logger.info('%s is editing a category (%s)' % (request.user, category.name))
            category_form = ToolCategoryForm(data = request.POST, 
                                             instance = category)
            if category_form.is_valid():
                category_form.save()
                logger.info('Category successfully edited')
                response = {'response': 'Kategori redigeret'}
            else:
                logger.info('Category not edited')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        else:
            logger.info('%s is creating a category (%s)' % (request.user, request.POST.get('name')))
            category_form = ToolCategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                logger.info('Category successfully created')
                response = {'response': 'Kategori oprettet'}
            else:
                logger.info('Category not created')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")
            
    category_id = request.GET.get('id')

    if category_id:
        category = get_object_or_404(ToolCategory, id = category_id)
        category_form = ToolCategoryForm(instance=category)
        context = {'form': category_form,
                   'object_type': 'category',
                   'id': category.id}
    else:
        category_form = ToolCategoryForm()
        context = {'form': category_form,
                   'object_type': 'category'}

    return render(request, 'form.html', context)

@login_required
def employee_form(request):
    if request.POST:
        employee_id = request.POST.get('id', 0)

        # Edit an existing employee
        if employee_id != 0:
            employee = get_object_or_404(Employee, id = employee_id)
            logger.info('%s is editing an employee (%s)' % (request.user, employee.name))
            employee_form = EmployeeForm(data = request.POST, 
                                         instance = employee)
            if employee_form.is_valid():
                employee_form.save()
                logger.info('Employee successfully created')
                response = {'response': 'Medarbejder redigeret'}
            else:
                logger.info('Employee not created')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        else:
            logger.debug('%s is creating a new employee: %s, %s, %s' %
                         (request.user,
                          request.POST.get('name'),
                          request.POST.get('email'),
                          request.POST.get('phone_number')))
            employee_form = EmployeeForm(request.POST)
            if employee_form.is_valid():
                employee_form.save()
                logger.debug('Employee successfully created')
                response = {'response': 'Medarbejder oprettet'}
            else:
                logger.debug('Employee not created')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")
            
    employee_id = request.GET.get('id')

    if employee_id:
        employee = get_object_or_404(Employee, id = employee_id)
        employee_form = EmployeeForm(instance=employee)
        context = {'form': employee_form,
                   'object_type': 'employee',
                   'id': employee.id}
    else:
        employee_form = EmployeeForm()
        context = {'form': employee_form,
                   'object_type': 'employee'}

    return render(request, 'form.html', context)

@login_required
def building_site_form(request):
    if request.POST:
        building_site_id = request.POST.get('id', 0)

        # Edit an existing building_site
        if building_site_id != 0:
            building_site = get_object_or_404(ConstructionSite, id = building_site_id)
            logger.info('%s is editing a building site (%s)' % (request.user, building_site.name))
            building_site_form = BuildingSiteForm(data = request.POST, 
                                         instance = building_site)
            if building_site_form.is_valid():
                building_site_form.save()
                logger.info('Building site successfully edited')
                response = {'response': 'Byggeplads redigeret'}
            else:
                logger.info('Building site not edited')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        else:
            logger.info('%s is creating a building site (%s)' % (request.user, request.POST.get('name')))
            building_site_form = BuildingSiteForm(request.POST)
            if building_site_form.is_valid():
                building_site_form.save()
                logger.info('Building site successfully created')
                response = {'response': 'Byggeplads oprettet'}
            else:
                logger.info('Building site not created')
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")
            
    building_site_id = request.GET.get('id')

    if building_site_id:
        building_site = get_object_or_404(ConstructionSite, id = building_site_id)
        building_site_form = BuildingSiteForm(instance=building_site)
        context = {'form': building_site_form,
                   'object_type': 'building_site',
                   'id': building_site.id}
    else:
        building_site_form = BuildingSiteForm()
        context = {'form': building_site_form,
                   'object_type': 'building_site'}

    return render(request, 'form.html', context)

@login_required
def loan_form(request):
	if request.POST:
		logger.info('%s is loaning %s to %s/%s' % (request.user, request.POST.get('tools'), request.POST.get('employee'), request.POST.get('construction_site')))
		loan_form = LoanForm(request.POST)
		if loan_form.is_valid():
			loan_form.save()
			logger.info('Tools loaned')
			response = {'response': 'Værktøj udlånt'}
		else:
			logger.info('Tools not loaned')
			response = {'response': 'Værktøj ikke udlånt'}
			
		return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")
	
	loan_form = LoanForm()
	context = {'form': loan_form, 'object_type': 'loan'}
	return render(request, 'form.html', context)

@login_required
def container_loan_form(request):
    if request.POST:
        logger.info('%s is container_loaning %s to %s/%s' % (request.user, request.POST.get('tools'), request.POST.get('employee'), request.POST.get('construction_site')))
        container_loan_form = ContainerLoanForm(request.POST)
        if container_loan_form.is_valid():
            container_loan_form.save()
            logger.info('Tools container_loaned')
            response = {'response': 'Værktøj udlånt'}
        else:
            logger.info('Tools not container_loaned')
            response = {'response': 'Værktøj ikke udlånt'}
            
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")
	
    container_loan_form = ContainerLoanForm()
    context = {'form': container_loan_form, 'object_type': 'container_loan'}
    return render(request, 'form.html', context)

@login_required
def tool_action(request):
    action = request.POST.get('action')
    object_ids = request.POST.get('object_ids', '')

    logger.info('Tool action started by %s: %s on tools %s' % (request.user,
                                                               action, 
                                                               object_ids))

    if object_ids != '':
        object_ids = object_ids.split(',')
    else:
        response = {'response': 'Intet værktøj valgt'}        
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    if action == 'loan':
        employee_id = request.POST.get('employee_id')
        try:
            employee = get_object_or_404(Employee, id = employee_id)
        except Http404:
            logger.error('Employee with id %s not found' % employee_id)
            raise Http404
    elif action == 'loan_single':
        employee = request.user

    success_tools = []
    success_tool_ids = []
    failure_tools = {}

    for object_id in object_ids:
        try:
            tool = get_object_or_404(Tool, id = object_id)
        except Http404:
            logger.error('Tool with id %s not found' % object_id)
        if action == 'service':
            if tool.service():
                success_tools.append(tool.name)
                success_tool_ids.append(tool.id)
                logger.info('Tool with id %s serviced' % tool.id)
            else:
                try:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE] = [tool.name]
                logger.info('Tool with id %s not serviced (not in store)' % tool.id)
        elif action == 'scrap':
            if tool.scrap():
                success_tools.append(tool.name)
                logger.info('Tool with id %s scrapped' % tool.id)
            else:
                try:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE] = [tool.name]
                logger.info('Tool with id %s not scrapped (not in store)' % tool.id)
        elif action == 'lost':
            if tool.lost():
                success_tools.append(tool.name)
                logger.info('Tool with id %s marked as lost' % tool.id)
            else:
                try:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE] = [tool.name]
                logger.info('Tool with id %s not marked as lost (not in store)' % tool.id)
        elif action == 'repair':
            if tool.repair():
                success_tools.append(tool.name)
                logger.info('Tool with id %s repaired' % tool.id)
            else:
                try:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE] = [tool.name]
                logger.info('Tool with id %s not repaired (not in store)' % tool.id)
        elif action == 'return':
            if request.user.is_admin() or tool.loaned_to == request.user or tool.location == 'Lager' or tool.location == 'Reparation' or tool.location == 'Kasseret' or tool.location == 'Bortkommet':
                if tool.end_loan():
                    success_tools.append(tool.name)
                    logger.info('Tool with id %s returned' % tool.id)
                else:
                    try:
                        failure_tools[TOOL_FAILURES.NOT_ON_LOAN].append(tool.name)
                    except KeyError:
                        failure_tools[TOOL_FAILURES.NOT_ON_LOAN] = [tool.name]
                    logger.info('Tool with id %s not returned (in store)' % tool.id)
            else:
                try:
                    failure_tools[TOOL_FAILURES.NO_RIGHTS].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NO_RIGHTS] = [tool.name]
                    logger.warning('Tool with id %s not returned (no rights)' % tool.id)
        elif action == 'delete':
            tool_name = tool.name
            logger.warning('Tool with id %s deleted' % tool.id)
            tool.delete()
            success_tools.append(tool_name)
        elif action == 'loan' or action == 'loan_single':
            if tool.loan(employee):
                success_tools.append(tool.name)
                logger.info('Tool with id %s loaned to %s' % (tool.id, employee.name))
            else:
                try:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE] = [tool.name]
                logger.info('Tool with id %s not loaned to %s (not in store)' % (tool.id, employee.name))

    # Generate success string
    success_string = ''
    for tool_name in success_tools:
        if tool_name == success_tools[0]:
            success_string = tool_name
        elif tool_name == success_tools[-1]:
            success_string += ' og ' + tool_name
        else:
            success_string += ', ' + tool_name

    # Generate failure string and append action to success string
    failure_string = ''
    if action == 'service':
        for key, val in failure_tools.items():
            for tool_name in failure_tools[key]:
                if tool_name == failure_tools[key][0]:
                    failure_string = tool_name
                elif tool_name == failure_tools[key][-1]:
                    failure_string += ' og ' + tool_name
                else:
                    failure_string += ', ' + tool_name
            if failure_tools.items():
                if key == TOOL_FAILURES.NOT_IN_STORE:
                    failure_string += ' blev ikke serviceret (værktøj ikke på lager)<br>'
        if success_tools:
            success_string += ' blev serviceret<br>'

    elif action == 'scrap':
        for key, val in failure_tools.items():
            for tool_name in failure_tools[key]:
                if tool_name == failure_tools[key][0]:
                    failure_string = tool_name
                elif tool_name == failure_tools[key][-1]:
                    failure_string += ' og ' + tool_name
                else:
                    failure_string += ', ' + tool_name
            if failure_tools.items():
                if key == TOOL_FAILURES.NOT_IN_STORE:
                    failure_string += ' blev ikke kasseret (værktøj ikke på lager)<br>'
        if success_tools:
            success_string += ' blev kasseret<br>'

    elif action == 'lost':
        for key, val in failure_tools.items():
            for tool_name in failure_tools[key]:
                if tool_name == failure_tools[key][0]:
                    failure_string = tool_name
                elif tool_name == failure_tools[key][-1]:
                    failure_string += ' og ' + tool_name
                else:
                    failure_string += ', ' + tool_name
            if failure_tools.items():
                if key == TOOL_FAILURES.NOT_IN_STORE:
                    failure_string += ' blev ikke markeret som bortkommet (værktøj ikke på lager)<br>'
        if success_tools:
            success_string += ' blev markeret som bortkommet<br>'

    elif action == 'repair':
        for key, val in failure_tools.items():
            for tool_name in failure_tools[key]:
                if tool_name == failure_tools[key][0]:
                    failure_string = tool_name
                elif tool_name == failure_tools[key][-1]:
                    failure_string += ' og ' + tool_name
                else:
                    failure_string += ', ' + tool_name
            if failure_tools.items():
                if key == TOOL_FAILURES.NOT_IN_STORE:
                    failure_string += ' blev ikke repareret (værktøj ikke på lager)<br>'
        if success_tools:
            success_string += ' blev repareret<br>'

    elif action == 'return':
        for key, val in failure_tools.items():
            for tool_name in failure_tools[key]:
                if tool_name == failure_tools[key][0]:
                    failure_string += tool_name
                elif tool_name == failure_tools[key][-1]:
                    failure_string += ' og ' + tool_name
                else:
                    failure_string += ', ' + tool_name
            if failure_tools.items():
                if key == TOOL_FAILURES.NOT_ON_LOAN:
                    failure_string += ' blev ikke afleveret (værktøj ikke udlånt)<br>'
                elif key == TOOL_FAILURES.NO_RIGHTS:
                    failure_string += ' blev ikke afleveret (ikke udlånt til dig)<br>'
        if success_tools:
            success_string += ' blev afleveret<br>'

    elif action == 'delete':
        if success_tools:
            success_string += ' blev slettet<br>'

    elif action == 'loan' or action == 'loan_single':
        for key, val in failure_tools.items():
            for tool_name in failure_tools[key]:
                if tool_name == failure_tools[key][0]:
                    failure_string = tool_name
                elif tool_name == failure_tools[key][-1]:
                    failure_string += ' og ' + tool_name
                else:
                    failure_string += ', ' + tool_name
            if failure_tools.items():
                if key == TOOL_FAILURES.NOT_IN_STORE:
                    failure_string += ' blev ikke udlånt (værktøj ikke på lager)<br>'
        if success_tools:
            success_string += ' blev udlånt<br>'

    response = {'response': success_string + failure_string,
                'success_tool_ids': success_tool_ids}

    if action == 'loan' or action == 'loan_single':
        handle_loan_messages(success_tools, employee)

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def model_action(request):
    action = request.POST.get('action')
    object_ids = request.POST.get('object_ids', '')

    logger.info('Model action started by %s: %s on models %s' % (request.user,
                                                                 action, 
                                                                 object_ids))

    if object_ids != '':
        object_ids = object_ids.split(',')
    else:
        logger.info('No models selected')
        response = {'response': 'Ingen modeller valgt'}        
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    for object_id in object_ids:
        try:
            model = get_object_or_404(ToolModel, id = object_id)
        except Http404:
            logger.error('Model with id %s not found' % object_id)
        if action == 'delete':
            model.delete()
            logger.info('Model with id %s deleted' % object_id)
            response = {'response': 'Model(ler) slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def container_action(request):
    action = request.POST.get('action')
    object_ids = request.POST.get('object_ids', '')

    logger.info('Container action started by %s: %s on containers %s' % (request.user, action, object_ids))

    if object_ids != '':
        object_ids = object_ids.split(',')
    else:
        logger.info('No containers selected')
        response = {'response': 'Ingen containere valgt'}        
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    for object_id in object_ids:
        try:
            container = get_object_or_404(Container, id = object_id)
        except Http404:
            logger.error('Container with id %s not found' % object_id)
        if action == 'delete':
            container.delete()
            logger.info('Container with id %s deleted' % object_id)
            response = {'response': 'Container(e) slettet'}
        elif action == 'make_inactive':
            container.is_active = False
            logger.info('Container with id %s marked as inactive' % object_id)
            container.save()
            response = {'response': 'Container(e) markeret som inaktiv(e)'}
        elif action == 'make_active':
            container.is_active = True
            logger.info('Container with id %s marked as active' % object_id)
            container.save()
            response = {'response': 'Container(e) markeret som aktiv(e)'}
        elif action == 'return':
            container.end_loan()
            logger.info('Container with id %s returned' % object_id)
            response = {'response': 'Container(e) markeret som afleveret'}
        
    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def category_action(request):
    action = request.POST.get('action')
    object_ids = request.POST.get('object_ids', '')

    logger.info('Category action started by %s: %s on categories %s' % (request.user, action, object_ids))

    if object_ids != '':
        object_ids = object_ids.split(',')
    else:
        logger.info('No categories selected')
        response = {'response': 'Ingen kategorier valgt'}        
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    for object_id in object_ids:
        try:
            category = get_object_or_404(ToolCategory, id = object_id)
        except Http404:
            logger.error('Category with id %s not found' % object_id)
        if action == 'delete':
            category.delete()
            logger.info('Category with id %s deleted' % object_id)
            response = {'response': 'Kategori(er) slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def construction_site_action(request):
    action = request.POST.get('action')
    object_ids = request.POST.get('object_ids', '')

    logger.info('Construction site action started by %s: %s on sites %s' % (request.user, action, object_ids))

    if object_ids != '':
        object_ids = object_ids.split(',')
    else:
        logger.info('No employees selected')
        response = {'response': 'Ingen byggepladser valgt'}
        return HttpResponse(simplejson.dumps(response),
                            mimetype='application/json')

    for object_id in object_ids:
        try:
            construction_site = get_object_or_404(ConstructionSite, 
                                                  id = object_id)
        except Http404:
            logger.error('Construction site with id %s not found', object_id)

        if action == 'delete':
            logger.warning('Construction site with id %s deleted' % object_id)
            construction_site.delete()
            response = {'response': 'Byggeplads(er) slettet'}
        elif action == 'make_inactive':
            construction_site.is_active = False
            logger.info('Construction site with id %s marked as inactive' % object_id)
            construction_site.save()
            response = {'response': 'Byggeplads(er) markeret som inaktiv(e)'}
        elif action == 'make_active':
            construction_site.is_active = True
            logger.info('Construction site with id %s marked as active' % object_id)
            construction_site.save()
            response = {'response': 'Byggeplads(er) markeret som aktiv(e)'}
            
    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def employee_action(request):
    action = request.POST.get('action')
    object_ids = request.POST.get('object_ids', '')

    logger.info('Employee action started by %s: %s on employees %s' % (request.user,
                                                                   action, 
                                                                   object_ids))

    if object_ids != '':
        object_ids = object_ids.split(',')
    else:
        logger.info('No employees selected')
        response = {'response': 'Ingen medarbejdere valgt'}        
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    for object_id in object_ids:
        try:
            employee = get_object_or_404(Employee, id = object_id)
        except Http404:
            logger.error('Employee with id %s not found' % object_id)

        if action == 'delete':
            logger.warning('Employee with id %s deleted' % object_id)
            employee.delete()
            response = {'response': 'Medarbejder(e) slettet'}
        elif action == 'make_inactive':
            employee.is_active = False
            logger.info('Employee with id %s marked as inactive' % object_id)
            employee.save()
            response = {'response': 'Medarbejder(e) markeret som inaktiv(e)'}
        elif action == 'make_active':
            employee.is_active = True
            logger.info('Employee with id %s marked as active' % object_id)
            employee.save()
            response = {'response': 'Medarbejder(e) markeret som aktiv(e)'}
        elif action == 'set_office_admin':
            employee.is_office_admin = True
            logger.info('Employee with id %s marked as office admin' % object_id)
            employee.save()
            response = {'response': 'Medarbejder(e) markeret som kontoradmin'}
        elif action == 'remove_office_admin':
            employee.is_office_admin = False
            logger.info('Employee with id %s removed as office admin' % object_id)
            employee.save()
            response = {'response': 'Medarbejder(e) fjernet som kontoradmin'}
        elif action == 'set_tool_admin':
            employee.is_tool_admin = True
            logger.info('Employee with id %s marked as tool admin' % object_id)
            employee.save()
            response = {'response': 'Medarbejder(e) markeret som værktøjsadmin'}
        elif action == 'remove_tool_admin':
            employee.is_tool_admin = False
            logger.info('Employee with id %s removed as tool admin' % object_id)
            employee.save()
            response = {'response': 'Medarbejder(e) fjernet som værktøjsadmin'}
        elif action == 'set_loan_flag':
            employee.is_loan_flagged = True
            logger.info('Employee with id %s marked as loan flagged' % object_id)
            employee.save()
            response = {'response': 'Medarbejder(e) markeret med låneflag'}
        elif action == 'remove_loan_flag':
            employee.is_loan_flagged = False
            logger.info('Employee with id %s removed as loan flagged' % object_id)
            employee.save()
            response = {'response': 'Medarbejder(e) fik fjernet låneflag'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def delete(request, class_to_delete):
    object_id = request.POST.get('id')
    logger.warning('%s is trying to delete %s with id %s' % (request.user,
                                                             class_to_delete.__name__,
                                                             object_id))

    if not request.user.is_admin():
        logger.error('%s does not have rights to delete' % (class_to_delete.__name__, 
                                                            object_id))
        raise Http404

    try:
        object_to_delete = get_object_or_404(class_to_delete, id = object_id)
    except Http404:
        logger.error('%s with id %s not found' % (class_to_delete.__name__, object_id))
        raise Http404
    
    name = object_to_delete.name
    object_to_delete.delete()
    logger.warning('%s with id %s deleted' % (class_to_delete.__name__, object_id))

    response = {'response': name + ' slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")
@login_required
def event_delete(request):
    event_id = request.GET.get('id')
    logger.warning('%s is trying to delete event with id %s' % (request.user,
                                                                event_id))
    if not request.user.is_admin():
        logger.error('Event not deleted, user has no rights')
        response = {'response': 'Du har ikke rettigheder til at slette begivenheden'}
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    try:
        event = get_object_or_404(Event, id = event_id)
    except Http404:
        logger.error('Event not found' % event_id)
        raise Http404

    # Dont allow deletion of creation events
    if event.event_type == 'Oprettelse':
        logger.error('Event not deleted, is a creation event' % event_id)
        response = {'response': 'Begivenheden kan ikke slettes, da det er en oprettelse'}
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")
        
    tool = event.tool
    event_type = event.event_type
    event.delete()
    logger.warning('Event deleted (type: %s)' % event.event_type)
    if event_type == 'Service':
        tool.update_last_service()
    elif event_type == 'Bortkommet' or event_type == 'Kasseret':
        tool.end_date = None
        tool.save()

    response = {'response': 'Begivenheden blev slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

def forgot_password(request):
    if request.POST:
        form = ForgotPasswordForm(data=request.POST)

        if form.is_valid():
            logger.info('%s is requesting a new password' % request.POST.get('email'))
            form.save()
            return HttpResponseRedirect(reverse('login'))
    else:
        form = ForgotPasswordForm()

    context = {'form': form}

    return render(request, 'forgot_password.html', context)

def reset_password(request, token):
    forgot_password_token = get_object_or_404(ForgotPasswordToken, token=token)
    user = forgot_password_token.user

    password = Employee.objects.make_random_password()
    user.set_password(password)
    user.save()

    message = ('Hej ' + user.name + '\n' +
               'Vi har nulstillet dit kodeord. Dit nye kodeord er ' +
               password + '. Du kan nu logge ind med dette kodeord og' +
               'brugernavnet ' + user.name + '.\n\n' +
               'MVH\n' +
               'ToolControl')

    user.send_mail('Kodeord nulstillet', message)

    forgot_password_token.delete()

    logger.info('Password reset for %s' % user.name)

    return HttpResponseRedirect(reverse('login'))

@login_required
def model_object(request):
    model_id = request.GET.get('id')
    model = get_object_or_404(ToolModel, id=model_id)

    response = {
        'model': serializers.serialize('json', [model,])
        }

    return HttpResponse(simplejson.dumps(response), 
                        mimetype='application/json')

def qr_code(request, pk):
    img = qrcode.make('http://skou.toolcontrol.dk/tools/%s/qr_action' % pk)
    response = HttpResponse(mimetype='image/png')
    img.save(response, 'PNG')
    return response

def qr_text(request, pk):
    tool = get_object_or_404(Tool, id=pk)
    context = {'tool': tool}
    return render(request, 'qr/qr.html', context)

def qr_action(request, pk):
    if request.user.is_authenticated():
        if request.user.is_admin():
            tool = get_object_or_404(Tool, id=pk)
            if tool.location == 'Lager':
                if request.POST:
                    form = QRLoanForm(tool=tool, data=request.POST)
                    if form.is_valid():
                        form.save()
                        context = {'message': 'Værktøjet blev udlånt',
                                   'status': 'success'}
                        return render(request, 'qr/success.html', context)
                else:
                    form = QRLoanForm(tool=tool)
            
                context = {'form': form}
                return render(request, 'qr/form.html', context)

            elif tool.location == 'Udlånt' or tool.location == 'Reparation':
                tool.end_loan()
                context = {'message': 'Værktøjet blev afleveret',
                           'status': 'success'}
                return render(request, 'qr/success.html', context)
            else:
                context = {'message': 'Værktøjet kan ikke udlånes, da det er kasseret eller bortkommet',
                           'status': 'failure'}
                return render(request, 'qr/success.html', context)

        else:
            tool = get_object_or_404(Tool, id=pk)
            if tool.location == 'Lager':
                tool.loan(request.user) 
                context = {'message': 'Værktøjet blev udlånt til %s' % request.user,
                           'status': 'success'}
                return render(request, 'qr/success.html', context)
            elif tool.location == 'Udlånt' or tool.location == 'Reparation':
                if tool.employee == request.user:
                    tool.end_loan()
                    context = {'message': 'Værktøjet blev afleveret',
                               'status': 'success'}
                else:
                    context = {'message': 'Du har ikke rettigheder til at aflevere værktøj udlånt til andre',
                               'status': 'failure'}
                return render(request, 'qr/success.html', context)
            else:
                context = {'message': 'Værktøjet kan ikke udlånes, da det er kasseret eller bortkommet',
                           'status': 'failure'}
                return render(request, 'qr/success.html', context)

    else:
        if request.POST:
            authentication_form = AuthenticationForm(data=request.POST)
            if authentication_form.is_valid():
                user = authentication_form.get_user()
                login(request, user)
                return HttpResponseRedirect('/tools/%s/qr_action' % pk)
        else:
            authentication_form = AuthenticationForm()

        context_dictionary = {'authentication_form': authentication_form}
        return render(request, 'qr/login.html', context_dictionary)

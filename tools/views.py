# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import logging
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

from tools.forms import BuildingSiteForm, CreateManyToolsForm, EmployeeForm 
from tools.forms import ForgotPasswordForm, LoanForm, SettingsForm, ToolForm
from tools.forms import ToolCategoryForm, ToolModelForm

from tools.models import ConstructionSite, Event, Employee, Tool, ForgotPasswordToken
from tools.models import ToolCategory, ToolModel

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
        }

    return render(request, 'stats.html', context_dictionary)

@login_required
def index(request):
    if request.POST:
        logger.info('%s is creating many tools' % request.user)
        add_many_form = CreateManyToolsForm(request.POST)
        if add_many_form.is_valid():
            add_many_form.save()
            logger.info('Many tools created successfully')
            add_many_form = CreateManyToolsForm()
        else:
            logger.info('Many tools not created')
    else:
        add_many_form = CreateManyToolsForm()

    context = {'employees': Employee.objects.filter(is_active=True).order_by('name'),
               'add_many_form': add_many_form}
    return render(request, 'index.html', context)

@login_required
def tool_list(request):
    search = request.GET.get('search', '')
    sorting = request.GET.get('sorting', 'name')

    if search:
        tools = Tool.objects.filter(Q(name__icontains=search) |
                                    Q(model__name__icontains=search) |
                                    Q(model__category__name__icontains=search) |
                                    Q(loaned_to__name__icontains=search) | 
                                    Q(location__iexact=search) |
                                    Q(secondary_name__icontains=search) |
                                    Q(invoice_number__icontains=search)).select_related('loaned_to').order_by(sorting)
        if sorting == 'location' or sorting == '-location':
            tools = tools.order_by(sorting, 'loaned_to__name')        
    else:
        tools = Tool.objects.all().select_related('loaned_to', 'model__category').order_by(sorting)
        if sorting == 'location' or sorting == '-location':
            tools = tools.order_by(sorting, 'loaned_to__name')

    context = {'tools': tools,
               'search': search}

    if sorting[0] != '-':
        context[sorting + '_sorting'] = '-'

    return render(request, 'tool_list.html', context)

@login_required
def model_list(request):
    if not request.user.is_tool_admin and not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    search = request.GET.get('search', '')
    sorting = request.GET.get('sorting', 'name')

    if search:
        models = ToolModel.objects.filter(Q(name__icontains=search) |
                                          Q(category__name__icontains=search)).order_by(sorting)
    else:
        models = ToolModel.objects.all().order_by(sorting)

    context = {'models': models,
               'search': search}

    # Reverse the sorting link
    if sorting[0] != '-':
        context[sorting + '_sorting'] = '-'

    return render(request, 'model_list.html', context)

@login_required
def category_list(request):
    if not request.user.is_tool_admin and not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    search = request.GET.get('search', '')
    sorting = request.GET.get('sorting', 'name')

    if search:
        categories = ToolCategory.objects.filter(name__icontains=search).order_by(sorting)
    else:
        categories = ToolCategory.objects.all().order_by(sorting)

    context = {'categories': categories,
               'search': search}

    if sorting[0] != '-':
        context[sorting + '_sorting'] = '-'

    return render(request, 'category_list.html', context)

@login_required
def employee_list(request):
    if not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    search = request.GET.get('search', '')
    sorting = request.GET.get('sorting', 'name')

    if search:
        if search == 'aktiv' or search == 'inaktive':
            employees = Employee.objects.filter(is_active=True).order_by(sorting)
        elif search == 'inaktiv' or search == 'inaktive':
            employees = Employee.objects.filter(is_active=False).order_by(sorting)
        else:
            employees = Employee.objects.filter(Q(name__icontains=search) |
                                              Q(phone_number__icontains=search) |
                                              Q(email__icontains=search)).order_by(sorting)
    else:
        employees = Employee.objects.all().order_by(sorting)
        
    context = {'employees': employees,
               'search': search}

    if sorting[0] != '-':
        context[sorting + '_sorting'] = '-'

    return render(request, 'employee_list.html', context)

@login_required
def building_site_list(request):
    if not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    search = request.GET.get('search', '')
    sorting = request.GET.get('sorting', 'name')

    if search:
        if search == "aktiv" or search == "aktive":
            building_sites = ConstructionSite.objects.filter(is_active=True).order_by(sorting)
        elif search == "inaktiv" or search == "inaktive":
            building_sites = ConstructionSite.objects.filter(is_active=False).order_by(sorting)
        else:
            building_sites = ConstructionSite.objects.filter(name__icontains=search).order_by(sorting)

    else:
        building_sites = ConstructionSite.objects.all().order_by(sorting)

    context = {'building_sites': building_sites,
               'search': search}

    if sorting[0] != '-':
        context[sorting + '_sorting'] = '-'

    return render(request, 'building_site_list.html', context)

@login_required
def event_list(request):
    tool_id = request.GET.get('tool_id')
    tool = get_object_or_404(Tool, id = tool_id)

    context = {'events': Event.objects.filter(tool=tool).order_by('start_date')}

    return render(request, 'event_list.html', context)

@login_required
def loan_list(request):
    loaner_id = request.GET.get('loaner_id')
    object_type = request.GET.get('object_type')
    print object_type
    
    if object_type == 'employee':
        employee = get_object_or_404(Employee, id = loaner_id)
        context = {'loans': Event.objects.filter(employee=employee).order_by('-start_date')}
    elif object_type == 'building_site':
        construction_site = get_object_or_404(ConstructionSite, id = loaner_id)
        context = {'loans': Event.objects.filter(construction_site=construction_site).order_by('-start_date')}

    return render(request, 'loan_list.html', context)

@login_required
def simple_tool_list(request):
    show_model = request.GET.get('show_model')

    if show_model == 'true':
        category_id = request.GET.get('category_id')
        category = get_object_or_404(ToolCategory, id = category_id)
        context = {'tools': Tool.objects.filter(model__category=category).order_by('name'),
                   'show_model': True}
    else:
        model_id = request.GET.get('model_id')
        model = get_object_or_404(ToolModel, id = model_id)
        context = {'tools': Tool.objects.filter(model=model).order_by('name'),
                   'show_model': False}
        
    return render(request, 'simple_tool_list.html', context)

@login_required
def tool_banner(request):
    context = {}
    return render(request, 'tool_banner.html', context)

@login_required
def model_banner(request):
    if not request.user.is_tool_admin and not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'model_banner.html', context)

@login_required
def category_banner(request):
    if not request.user.is_tool_admin and not request.user.is_office_admin:
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
		print request.POST
		logger.info('%s is loaning %s to %s/%s' % (request.user, request.POST.get('tools'), request.POST.get('employee'), request.POST.get('construction_site')))
		loan_form = LoanForm(request.POST)
		if loan_form.is_valid():
			loan_form.save()
			logger.info('Tools loaned')
			response = {'response': 'Værktøj udlånt'}
		else:
			logger.info('Tools not loaned')
			print loan_form
			response = {'response': 'Værktøj ikke udlånt'}
			
		return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")
	
	loan_form = LoanForm()
	context = {'form': loan_form, 'object_type': 'loan'}
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
def tool_delete(request):
    tool_id = request.POST.get('id')
    logger.warning('%s is trying to delete tool with id %s' % (request.user,
                                                               tool_id))
    try:
        tool = get_object_or_404(Tool, id = tool_id)
    except Http404:
        logger.error('Tool with id %s not found' % tool_id)
        raise Http404
    tool_name = tool.name
    tool.delete()
    logger.warning('Tool with id %s deleted' % tool_id)

    response = {'response': tool_name+' slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def model_delete(request):
    model_id = request.POST.get('id')
    logger.info('%s is trying to delete model with id %s' % (request.user,
                                                             model_id))
    try:
        model = get_object_or_404(ToolModel, id = model_id)
    except Http404:
        logger.error('Model with id %s not found' % model_id)
        raise Http404

    model_name = model.name
    model.delete()
    logger.info('Model with id %s deleted' % model_id)

    response = {'response': model_name+' slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def category_delete(request):
    category_id = request.POST.get('id')
    logger.info('%s is trying to delete category with id %s' % (request.user,
                                                                category_id))
    try:
        category = get_object_or_404(ToolCategory, id = category_id)
    except Http404:
        logger.error('Category with id %s not found' % category_id)
        raise Http404

    category_name = category.name
    category.delete()
    logger.info('Category with id %s deleted' % category_id)

    response = {'response': category_name+' slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def employee_delete(request):
    employee_id = request.POST.get('id')
    logger.info('%s is trying to delete employee with id %s' % (request.user,
                                                              employee_id))
    try:
        employee = get_object_or_404(Employee, id = employee_id)
    except Http404:
        logger.error('Employee with id %s not found' % employee_id)
        raise Http404

    employee_name = employee.name
    employee.delete()
    logger.info('Employee with id %s deleted' % employee_id)

    response = {'response': employee_name+' slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def construction_site_delete(request):
    construction_site_id = request.POST.get('id')
    logger.info('%s is trying to delete construction site with id %s' % (request.user,
                                                              construction_site_id))
    try:
        construction_site = get_object_or_404(ConstructionSite, id = construction_site_id)
    except Http404:
        logger.error('ConstructionSite with id %s not found' % construction_site_id)
        raise Http404

    construction_site_name = construction_site.name
    construction_site.delete()
    logger.info('ConstructionSite with id %s deleted' % construction_site_id)

    response = {'response': construction_site_name+' slettet'}

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

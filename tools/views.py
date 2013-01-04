# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.urlresolvers import reverse
from django.db.models import Avg, Sum, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page
from django.utils import simplejson

from tools.forms import BuildingSiteForm, CreateManyToolsForm, EmployeeForm 
from tools.forms import ForgotPasswordForm, SettingsForm, ToolForm
from tools.forms import ToolCategoryForm, ToolModelForm

from tools.models import Event, Loaner, Tool, ForgotPasswordToken
from tools.models import ToolCategory, ToolModel

from toolbase.enums import TOOL_FAILURES
from toolbase.utils import handle_loan_messages

def login_view(request):
    if request.POST:
        authentication_form = AuthenticationForm(data=request.POST)
        if authentication_form.is_valid():
            user = authentication_form.get_user()
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
    else:
        authentication_form = AuthenticationForm()

    context_dictionary = {'authentication_form': authentication_form}
    return render(request, 'login.html', context_dictionary)

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

@login_required
def settings(request):
    password_change_form = PasswordChangeForm(request.user)
    settings_form = SettingsForm(instance=request.user)

    if request.POST:
        form = request.POST.get('form')
        if form == 'password_change':
            password_change_form = PasswordChangeForm(user = request.user,
                                                      data = request.POST)
            if password_change_form.is_valid():
                password_change_form.save()
                password_change_form = PasswordChangeForm(request.user)
        elif form == 'settings':
            settings_form = SettingsForm(instance = request.user,
                                         data = request.POST)
            if settings_form.is_valid():
                settings_form.save()
                
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
        add_many_form = CreateManyToolsForm(request.POST)
        if add_many_form.is_valid():
            add_many_form.save()
            add_many_form = CreateManyToolsForm()
    else:
        add_many_form = CreateManyToolsForm()

    context = {'loaners': Loaner.objects.filter(is_active=True).order_by('name'),
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
@cache_page(60 * 15)
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
@cache_page(60 * 15)
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
            employees = Loaner.objects.filter(is_employee=True,
                                              is_active=True).order_by(sorting)
        elif search == 'inaktiv' or search == 'inaktive':
            employees = Loaner.objects.filter(is_employee=True,
                                              is_active=False).order_by(sorting)
        else:
            employees = Loaner.objects.filter(Q(is_employee=True) & 
                                              Q(name__icontains=search) |
                                              Q(phone_number__icontains=search) |
                                              Q(email__icontains=search)).order_by(sorting)
    else:
        employees = Loaner.objects.filter(is_employee=True).order_by(sorting)
        
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
            building_sites = Loaner.objects.filter(is_employee=False,
                                                   is_active=True).order_by(sorting)
        elif search == "inaktiv" or search == "inaktive":
            building_sites = Loaner.objects.filter(is_employee=False,
                                                   is_active=False).order_by(sorting)
        else:
            building_sites = Loaner.objects.filter(is_employee=False,
                                                   name__icontains=search).order_by(sorting)

    else:
        building_sites = Loaner.objects.filter(is_employee=False).order_by(sorting)

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
def loaner_list(request):
    context = {'loaners': Loaner.objects.filter(is_active=True).order_by('name')}
    return render(request, 'loaner_list.html', context)

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
            tool_form = ToolForm(data = request.POST, instance = tool)

            if tool_form.is_valid():
                new_tool = tool_form.save()
                tool_form = ToolForm()

                response = {'response': 'Værktøj redigeret'}
            else:
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        # Create new tool
        else:
            tool_form = ToolForm(request.POST)
            if tool_form.is_valid():
                tool = tool_form.save()
                event = Event(event_type="Oprettelse", tool=tool)
                event.save()
                
                response = {'response': 'Værktøj oprettet'}
            else:
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
            model_form = ToolModelForm(data = request.POST, instance = model)

            if model_form.is_valid():
                new_model = model_form.save()
                model_form = ToolModelForm()

                response = {'response': 'Model redigeret'}
            else:
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        else:
            model_form = ToolModelForm(request.POST)
            if model_form.is_valid():
                model = model_form.save()
                model_form = ToolModelForm()
            
                response = {'response': 'Model oprettet'}
            else:
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
            category_form = ToolCategoryForm(data = request.POST, 
                                             instance = category)
            if category_form.is_valid():
                category_form.save()
                response = {'response': 'Kategori redigeret'}
            else:
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        else:
            category_form = ToolCategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                response = {'response': 'Kategori oprettet'}
            else:
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
            employee = get_object_or_404(Loaner, id = employee_id)
            employee_form = EmployeeForm(data = request.POST, 
                                         instance = employee)
            if employee_form.is_valid():
                employee_form.save()
                response = {'response': 'Medarbejder redigeret'}
            else:
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        else:
            employee_form = EmployeeForm(request.POST)
            if employee_form.is_valid():
                employee_form.save()
                response = {'response': 'Medarbejder oprettet'}
            else:
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")
            
    employee_id = request.GET.get('id')

    if employee_id:
        employee = get_object_or_404(Loaner, id = employee_id)
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
            building_site = get_object_or_404(Loaner, id = building_site_id)
            building_site_form = BuildingSiteForm(data = request.POST, 
                                         instance = building_site)
            if building_site_form.is_valid():
                building_site_form.save()
                response = {'response': 'Byggeplads redigeret'}
            else:
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        else:
            building_site_form = BuildingSiteForm(request.POST)
            if building_site_form.is_valid():
                building_site_form.save()
                response = {'response': 'Byggeplads oprettet'}
            else:
                response = {'response': 'Et eller flere af de påkrævede felter er ikke udfyldt korrekt'}

        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")
            
    building_site_id = request.GET.get('id')

    if building_site_id:
        building_site = get_object_or_404(Loaner, id = building_site_id)
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
def tool_action(request):
    action = request.POST.get('action')
    object_ids = request.POST.get('object_ids', '')

    if object_ids != '':
        object_ids = object_ids.split(',')
    else:
        response = {'response': 'Intet værktøj valgt'}        
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    if action == 'loan':
        loaner_id = request.POST.get('loaner_id')
        loaner = get_object_or_404(Loaner, id = loaner_id)
    elif action == 'loan_single':
        loaner = request.user

    success_tools = []
    success_tool_ids = []
    failure_tools = {}

    for object_id in object_ids:
        tool = get_object_or_404(Tool, id = object_id)
        if action == 'service':
            if tool.service():
                success_tools.append(tool.name)
                success_tool_ids.append(tool.id)
            else:
                try:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE] = [tool.name]
        elif action == 'scrap':
            if tool.scrap():
                success_tools.append(tool.name)
            else:
                try:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE] = [tool.name]
        elif action == 'lost':
            if tool.lost():
                success_tools.append(tool.name)
            else:
                try:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE] = [tool.name]
        elif action == 'repair':
            if tool.repair():
                success_tools.append(tool.name)
            else:
                try:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE] = [tool.name]
        elif action == 'return':
            if request.user.is_admin() or tool.loaned_to == request.user or tool.location == 'Lager' or tool.location == 'Reparation' or tool.location == 'Kasseret' or tool.location == 'Bortkommet':
                if tool.end_loan():
                    success_tools.append(tool.name)
                else:
                    try:
                        failure_tools[TOOL_FAILURES.NOT_ON_LOAN].append(tool.name)
                    except KeyError:
                        failure_tools[TOOL_FAILURES.NOT_ON_LOAN] = [tool.name]
            else:
                try:
                    failure_tools[TOOL_FAILURES.NO_RIGHTS].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NO_RIGHTS] = [tool.name]
        elif action == 'delete':
            tool_name = tool.name
            tool.delete()
            success_tools.append(tool_name)
        elif action == 'loan' or action == 'loan_single':
            if tool.loan(loaner):
                success_tools.append(tool.name)
            else:
                try:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE].append(tool.name)
                except KeyError:
                    failure_tools[TOOL_FAILURES.NOT_IN_STORE] = [tool.name]

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
        handle_loan_messages(success_tools, loaner)

    print response
    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def model_action(request):
    action = request.POST.get('action')
    object_ids = request.POST.get('object_ids', '')

    if object_ids != '':
        object_ids = object_ids.split(',')
    else:
        response = {'response': 'Ingen modeller valgt'}        
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    for object_id in object_ids:
        model = get_object_or_404(ToolModel, id = object_id)
        if action == 'delete':
            model.delete()
            response = {'response': 'Model(ler) slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def category_action(request):
    action = request.POST.get('action')
    object_ids = request.POST.get('object_ids', '')

    if object_ids != '':
        object_ids = object_ids.split(',')
    else:
        response = {'response': 'Ingen kategorier valgt'}        
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    for object_id in object_ids:
        category = get_object_or_404(ToolCategory, id = object_id)
        if action == 'delete':
            category.delete()
            response = {'response': 'Kategori(er) slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def loaner_action(request):
    action = request.POST.get('action')
    object_ids = request.POST.get('object_ids', '')

    if object_ids != '':
        object_ids = object_ids.split(',')
    else:
        response = {'response': 'Ingen låner valgt'}        
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    for object_id in object_ids:
        loaner = get_object_or_404(Loaner, id = object_id)
        if action == 'delete':
            loaner.delete()
            response = {'response': 'Låner(e) slettet'}
        elif action == 'make_inactive':
            loaner.is_active = False
            loaner.save()
            response = {'response': 'Låner(e) markeret som inaktiv(e)'}
        elif action == 'make_active':
            loaner.is_active = True
            loaner.save()
            response = {'response': 'Låner(e) markeret som aktiv(e)'}
        elif action == 'set_office_admin':
            loaner.is_office_admin = True
            loaner.save()
            response = {'response': 'Låner(e) markeret som kontoradmin'}
        elif action == 'remove_office_admin':
            loaner.is_office_admin = False
            loaner.save()
            response = {'response': 'Låner(e) fjernet som kontoradmin'}
        elif action == 'set_tool_admin':
            loaner.is_tool_admin = True
            loaner.save()
            response = {'response': 'Låner(e) markeret som værktøjsadmin'}
        elif action == 'remove_tool_admin':
            loaner.is_tool_admin = False
            loaner.save()
            response = {'response': 'Låner(e) fjernet som værktøjsadmin'}
        elif action == 'set_loan_flag':
            loaner.is_loan_flagged = True
            loaner.save()
            response = {'response': 'Låner(e) markeret med låneflag'}
        elif action == 'remove_loan_flag':
            loaner.is_loan_flagged = False
            loaner.save()
            response = {'response': 'Låner(e) fik fjernet låneflag'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def tool_delete(request):
    tool_id = request.POST.get('id')
    tool = get_object_or_404(Tool, id = tool_id)
    tool_name = tool.name
    tool.delete()

    response = {'response': tool_name+' slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def model_delete(request):
    model_id = request.POST.get('id')
    model = get_object_or_404(ToolModel, id = model_id)
    model_name = model.name
    model.delete()

    response = {'response': model_name+' slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def category_delete(request):
    category_id = request.POST.get('id')
    category = get_object_or_404(ToolCategory, id = category_id)
    category_name = category.name
    category.delete()

    response = {'response': category_name+' slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def loaner_delete(request):
    loaner_id = request.POST.get('id')
    loaner = get_object_or_404(Loaner, id = loaner_id)
    loaner_name = loaner.name
    loaner.delete()

    response = {'response': loaner_name+' slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def event_delete(request):
    if not request.user.is_admin():
        response = {'response': 'Du har ikke rettigheder til at slette begivenheden'}
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    event_id = request.GET.get('id')
    event = get_object_or_404(Event, id = event_id)

    # Dont allow deletion of creation events
    if event.event_type == 'Oprettelse':
        response = {'response': 'Begivenheden kan ikke slettes, da det er en oprettelse'}
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")
        
    tool = event.tool
    event_type = event.event_type
    event.delete()
    if event_type == 'Service':
        tool.update_last_service()

    response = {'response': 'Begivenheden blev slettet'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

def forgot_password(request):
    if request.POST:
        form = ForgotPasswordForm(data=request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('login'))
    else:
        form = ForgotPasswordForm()

    context = {'form': form}

    return render(request, 'forgot_password.html', context)

def reset_password(request, token):
    forgot_password_token = get_object_or_404(ForgotPasswordToken, token=token)
    user = forgot_password_token.user

    password = Loaner.objects.make_random_password()
    user.set_password(password)
    user.save()

    message = ('Hej ' + user.name + '\n' +
               'Vi har nulstillet dit kodeord. Dit nye kodeord er ' +
               password + '. Du kan nu logge ind med dette kodeord og' +
               'brugernavnet ' + user.name + '.\n\n' +
               'MVH\n' +
               'ToolBase for SkouGruppen A/S')

    user.send_mail('Kodeord nulstillet', message)

    forgot_password_token.delete()

    return HttpResponseRedirect(reverse('login'))

def tool_print(request, search):
    if search:
        tools = Tool.objects.filter(Q(name__icontains=search) |
                                    Q(model__name__icontains=search) |
                                    Q(model__category__name__icontains=search) |
                                    Q(loaned_to__name__icontains=search) | 
                                    Q(location__iexact=search) |
                                    Q(secondary_name__icontains=search) |
                                    Q(invoice_number__icontains=search)).select_related('loaned_to')
    else:
        tools = Tool.objects.all().select_related('loaned_to', 'model__category')

    context = {'tools': tools,
               'search': search}

    return render(request, 'tool_print.html', context)

def model_print(request, search):
    if not request.user.is_admin():
        return HttpResponse('Du kan ikke se denne side')

    if search:
        models = ToolModel.objects.filter(Q(name__icontains=search) |
                                          Q(category__name__icontains=search))
    else:
        models = ToolModel.objects.all()

    context = {'models': models,
               'search': search}

    return render(request, 'model_print.html', context)

@login_required
def category_print(request, search):
    if not request.user.is_admin():
        return HttpResponse('Du kan ikke se denne side')

    if search:
        categories = ToolCategory.objects.filter(name__icontains=search)
    else:
        categories = ToolCategory.objects.all()

    context = {'categories': categories,
               'search': search}

    return render(request, 'category_print.html', context)

@login_required
def employee_print(request, search):
    if not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    if search:
        if search == 'aktiv' or search == 'inaktive':
            employees = Loaner.objects.filter(is_employee=True,
                                              is_active=True)
        elif search == 'inaktiv' or search == 'inaktive':
            employees = Loaner.objects.filter(is_employee=True,
                                              is_active=False)
        else:
            employees = Loaner.objects.filter(Q(is_employee=True) & 
                                              Q(name__icontains=search) |
                                              Q(phone_number__icontains=search) |
                                              Q(email__icontains=search))
    else:
        employees = Loaner.objects.filter(is_employee=True)
        
    context = {'employees': employees,
               'search': search}

    return render(request, 'employee_print.html', context)

@login_required
def building_site_print(request, search):
    if not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    if search:
        if search == "aktiv" or search == "aktive":
            building_sites = Loaner.objects.filter(is_employee=False,
                                                   is_active=True)
        elif search == "inaktiv" or search == "inaktive":
            building_sites = Loaner.objects.filter(is_employee=False,
                                                   is_active=False)
        else:
            building_sites = Loaner.objects.filter(is_employee=False,
                                                   name__icontains=search)

    else:
        building_sites = Loaner.objects.filter(is_employee=False)

    context = {'building_sites': building_sites,
               'search': search}

    return render(request, 'building_site_print.html', context)

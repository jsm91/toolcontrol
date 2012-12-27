# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.urlresolvers import reverse
from django.db.models import Avg, Sum, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import simplejson

from tools.forms import BuildingSiteForm, CreateManyToolsForm, EmployeeForm 
from tools.forms import SettingsForm, ToolForm, ToolCategoryForm, ToolModelForm
from tools.forms import Loaner, Tool, ToolCategory, ToolModel

from tools.models import Event

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
    return render(request, 'tools/login.html', context_dictionary)

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

    return render(request, 'tools/settings.html', context_dictionary)

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

    return render(request, 'tools/stats.html', context_dictionary)

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
    return render(request, 'tools/index.html', context)

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
    else:
        tools = Tool.objects.all().select_related('loaned_to', 'model__category').order_by(sorting)

    context = {'tools': tools,
               'search': search}

    if sorting[0] != '-':
        context[sorting + '_sorting'] = '-'

    return render(request, 'tools/tool_list.html', context)

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

    return render(request, 'tools/model_list.html', context)

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

    return render(request, 'tools/category_list.html', context)

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

    return render(request, 'tools/employee_list.html', context)

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
            building_sites.filter(is_active=False)
        elif search == "inaktiv" or search == "inaktive":
            building_sites = Loaner.objects.filter(is_employee=False,
                                                   is_active=False).order_by(sorting)
            building_sites.filter(is_active=False)
        else:
            building_sites = Loaner.objects.filter(is_employee=False,
                                                   name__icontains=search).order_by(sorting)

    else:
        building_sites = Loaner.objects.filter(is_employee=False).order_by(sorting)

    context = {'building_sites': building_sites,
               'search': search}

    if sorting[0] != '-':
        context[sorting + '_sorting'] = '-'

    return render(request, 'tools/building_site_list.html', context)

@login_required
def event_list(request):
    tool_id = request.GET.get('tool_id')
    tool = get_object_or_404(Tool, id = tool_id)

    context = {'events': Event.objects.filter(tool=tool).order_by('start_date')}

    return render(request, 'tools/event_list.html', context)

@login_required
def loaner_list(request):
    context = {'loaners': Loaner.objects.filter(is_active=True).order_by('name')}
    return render(request, 'tools/loaner_list.html', context)

@login_required
def tool_banner(request):
    context = {}
    return render(request, 'tools/tool_banner.html', context)

@login_required
def model_banner(request):
    if not request.user.is_tool_admin and not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'tools/model_banner.html', context)

@login_required
def category_banner(request):
    if not request.user.is_tool_admin and not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'tools/category_banner.html', context)

@login_required
def employee_banner(request):
    if not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'tools/employee_banner.html', context)

@login_required
def building_site_banner(request):
    if not request.user.is_office_admin:
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'tools/building_site_banner.html', context)

@login_required
def tool_form(request):
    if request.POST:
        tool_id = request.POST.get('id', 0)

        # Edit an existing tool
        if tool_id != 0:
            tool = get_object_or_404(Tool, id = tool_id)
            tool_form = ToolForm(data = request.POST, instance = tool)

            # Save old model, category and price to update stats properly
            old_tool_model = tool.model
            old_tool_category = tool.model.category
            old_tool_price = tool.price

            if tool_form.is_valid():
                new_tool = tool_form.save()
                tool_form = ToolForm()

                # Update stats
                if old_tool_model != new_tool.model:
                    old_tool_model.number_of_tools -= 1
                    old_tool_model.total_price -= old_tool_price
                    old_tool_model.save()
                    new_tool.model.number_of_tools += 1
                    new_tool.model.total_price += new_tool.price
                    new_tool.model.save()
                if old_tool_category != new_tool.model.category:
                    old_tool_category.number_of_tools -= 1
                    old_tool_category.total_price -= old_tool_price
                    old_tool_category.save()
                    new_tool.model.category.number_of_tools += 1
                    new_tool.model.category.total_price += new_tool.price
                    new_tool.model.category.save()

                response = {'response': 'Værktøj redigeret'}

        # Create new tool
        else:
            tool_form = ToolForm(request.POST)
            if tool_form.is_valid():
                tool = tool_form.save()
                event = Event(event_type="Oprettelse", tool=tool)
                event.save()
                
                tool.model.total_price += tool.price
                tool.model.number_of_tools += 1
                tool.model.save()

                tool.model.category.total_price += tool.price
                tool.model.category.number_of_tools += 1
                tool.model.category.save()
            
                response = {'response': 'Værktøj oprettet'}

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

    return render(request, 'tools/form.html', context)

@login_required
def model_form(request):
    if request.POST:
        model_id = request.POST.get('id', 0)

        # Edit an existing model
        if model_id != 0:
            model = get_object_or_404(ToolModel, id = model_id)
            model_form = ToolModelForm(data = request.POST, instance = model)

            # Save old category to update stats correct
            old_tool_category = model.category
            if model_form.is_valid():
                new_model = model_form.save()
                model_form = ToolModelForm()

                # Update stats
                if new_model.category != old_tool_category:
                    old_tool_category.number_of_models -= 1
                    old_tool_category.number_of_tools -= new_model.number_of_tools
                    old_tool_category.total_price -= new_model.total_price
                    old_tool_category.save()

                    new_model.category.number_of_models += 1
                    new_model.category.number_of_tools += new_model.number_of_tools
                    new_model.category.total_price += new_model.total_price
                    new_model.category.save()

            response = {'response': 'Model redigeret'}

        else:
            model_form = ToolModelForm(request.POST)
            if model_form.is_valid():
                model = model_form.save()
                model_form = ToolModelForm()
            
                model.category.number_of_models += 1
                model.category.save()
        
            response = {'response': 'Model oprettet'}
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

    return render(request, 'tools/form.html', context)

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
            category_form = ToolCategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
        
            response = {'response': 'Kategori oprettet'}
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

    return render(request, 'tools/form.html', context)

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
            response = {'response': 'Kategori redigeret'}

        else:
            employee_form = EmployeeForm(request.POST)
            if employee_form.is_valid():
                employee_form.save()
        
            response = {'response': 'Kategori oprettet'}
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

    return render(request, 'tools/form.html', context)

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
            response = {'response': 'Kategori redigeret'}

        else:
            building_site_form = BuildingSiteForm(request.POST)
            if building_site_form.is_valid():
                building_site_form.save()
        
            response = {'response': 'Kategori oprettet'}
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

    return render(request, 'tools/form.html', context)

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

    tools = []

    for object_id in object_ids:
        tool = get_object_or_404(Tool, id = object_id)
        if action == 'service':
            tool.service()
            response = {'response': 'Værktøj markeret som serviceret'}
        elif action == 'scrap':
            tool.scrap()
            response = {'response': 'Værktøj markeret som kasseret'}
        elif action == 'lost':
            tool.lost()
            response = {'response': 'Værktøj markeret som bortkommet'}
        elif action == 'repair':
            tool.repair()
            response = {'response': 'Værktøj makeret som til reparation'}
        elif action == 'return':
            if request.user.is_tool_admin or request.user.is_office_admin:
                tool.end_loan()
            elif tool.loaned_to == request.user:
                tool.end_loan()
            response = {'response': 'Værktøj markeret som afleveret'}
        elif action == 'delete':
            tool.delete()
            response = {'response': 'Værktøj slettet'}
        elif action == 'loan' or action == 'loan_single':
            tool.loan(loaner)
            tools.append(tool)
            response = {'response': 'Værktøj markeret som udlånt'}

    if action == 'loan' or action == 'loan_single':
        handle_loan_messages(tools, loaner)

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
    tool_id = request.GET.get('id')
    tool = get_object_or_404(Tool, id = tool_id)
    tool.delete()

    response = {'response': 'Gennemført'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def model_delete(request):
    model_id = request.GET.get('id')
    model = get_object_or_404(ToolModel, id = model_id)
    model.delete()

    response = {'response': 'Gennemført'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def category_delete(request):
    category_id = request.GET.get('id')
    category = get_object_or_404(ToolCategory, id = category_id)
    category.delete()

    response = {'response': 'Gennemført'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

@login_required
def loaner_delete(request):
    loaner_id = request.GET.get('id')
    loaner = get_object_or_404(Loaner, id = loaner_id)
    loaner.delete()

    response = {'response': 'Gennemført'}

    return HttpResponse(simplejson.dumps(response), 
                        mimetype="application/json")

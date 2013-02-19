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
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.generic import ListView
from django.views.generic.edit import FormView

from tools.forms import BuildingSiteForm, ContainerForm, ContainerLoanForm
from tools.forms import CreateManyToolsForm, EmployeeForm, ForgotPasswordForm
from tools.forms import LoanForm, QRLoanForm, ReservationForm, SettingsForm
from tools.forms import ToolForm, ToolCategoryForm, ToolModelForm

from tools.models import ConstructionSite, Container, Event, Employee, Tool
from tools.models import ForgotPasswordToken, Reservation, ToolCategory
from tools.models import ToolModel

from toolcontrol.enums import verbose_action, MESSAGES
from toolcontrol.utils import handle_loan_messages, make_message
from toolcontrol.utils import pretty_concatenate

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
    lost_tool_count = Tool.objects.filter(location='Bortkommet',
                                          model__category__customer=request.user.customer).count()
    scrapped_tool_count = Tool.objects.filter(location='Kasseret',
                                          model__category__customer=request.user.customer).count()
    
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

    alive_tools = Tool.objects.filter(end_date__isnull=True,
                                      model__category__customer=request.user.customer)
    timedeltas = [datetime.date.today() - tool.buy_date for tool in alive_tools]
    try:
        average_age = (sum(timedeltas, datetime.timedelta(0)) / alive_tools.count()).days
    except ZeroDivisionError:
        average_age = 0

    dead_tools = Tool.objects.filter(end_date__isnull=False,
                                     model__category__customer=request.user.customer)
    timedeltas = [tool.end_date - tool.buy_date for tool in dead_tools]
    try:
        average_life = (sum(timedeltas, datetime.timedelta(0)) / dead_tools.count()).days
    except ZeroDivisionError:
        average_life = 0

    context_dictionary = {
        'tool_count': Tool.objects.filter(model__category__customer=request.user.customer).count(),
        'model_count': ToolModel.objects.filter(category__customer=request.user.customer).count(),
        'category_count': ToolCategory.objects.filter(customer=request.user.customer).count(),
        'sum_price_tools': Tool.objects.filter(model__category__customer=request.user.customer).aggregate(Sum('price')),
        'avg_price_tools': Tool.objects.filter(model__category__customer=request.user.customer).aggregate(Avg('price')),
        'avg_price_models': ToolModel.objects.filter(category__customer=request.user.customer).aggregate(Avg('price')),
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
                                        Q(location__name__icontains=search),
                                        customer=self.request.user.customer).select_related('location').order_by(ordering)

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
                                   Q(invoice_number__icontains=search),
                                   model__category__customer=self.request.user.customer).select_related('loaned_to').order_by(ordering)

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
                                        Q(category__name__icontains=search),
                                        category__customer=self.request.user.customer).order_by(ordering)

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

        return ToolCategory.objects.filter(customer=self.request.user.customer,
                                           name__icontains=search).order_by(ordering)

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
            return Employee.objects.filter(customer=self.request.user.customer,
                                           is_active=True).order_by(sorting)
        elif search == 'inaktiv' or search == 'inaktive':
            return Employee.objects.filter(customer=self.request.user.customer,
                                           is_active=False).order_by(sorting)
        else:
            return Employee.objects.filter(Q(name__icontains=search) |
                                           Q(phone_number__icontains=search) |
                                           Q(email__icontains=search),
                                           customer=self.request.user.customer).order_by(ordering)

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
            return ConstructionSite.objects.filter(customer=self.request.user.customer,
                                                   is_active=True).order_by(sorting)
        elif search == 'inaktiv' or search == 'inaktive':
            return ConstructionSite.objects.filter(customer=self.request.user.customer,
                                                   is_active=False).order_by(sorting)
        else:
            return ConstructionSite.objects.filter(customer=self.request.user.customer,
                                                   name__icontains=search).order_by(ordering)

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

        return tool.event_set.all().order_by('start_date')

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)

        tool_id = self.request.GET.get('tool_id')
        tool = get_object_or_404(Tool, id = tool_id)

        context['reservations'] = tool.reservation_set.filter(end_date__gte=datetime.datetime.now())

        return context

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
    if not request.user.is_admin:
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'model_banner.html', context)

@login_required
def category_banner(request):
    if not request.user.is_admin:
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'category_banner.html', context)

@login_required
def employee_banner(request):
    if not request.user.is_admin:
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'employee_banner.html', context)

@login_required
def building_site_banner(request):
    if not request.user.is_admin:
        return HttpResponse('Du kan ikke se denne side')

    context = {}
    return render(request, 'building_site_banner.html', context)

@login_required
def form(request, class_name, form_name):
    if request.POST:
        obj_id = request.POST.get('id')

        if obj_id is not None:
            obj = get_object_or_404(class_name, id = obj_id)
            logger.info('%s is editing a %s (%s)' % (request.user, 
                                                     class_name.__name__,
                                                     obj.name))
            form = form_name(data = request.POST, instance = obj)

            if form.is_valid():
                form.save(customer=request.user.customer)
                logger.info('%s edited successfully' % class_name.__name__)
                form = form_name()

                response = {'status': 'success',
                            'response': 'Objekt redigeret'}
            else:
                logger.info('%s not edited' % class_name.__name__)
                context = {'form': form,
                           'object_type': class_name.verbose_name}
                response = {'status': 'failure',
                            'response': render_to_string('form.html', RequestContext(request, context))}

        else:
            logger.info('%s is creating a %s (%s)' % (request.user,
                                                      class_name.__name__,
                                                      request.POST.get('name')))
            form = form_name(request.POST)
            if form.is_valid():
                obj = form.save(customer=request.user.customer)
                logger.info('%s successfully created' % class_name.__name__)

                if isinstance(obj, Tool):
                    event = Event(event_type="Oprettelse", tool=obj)
                    event.save()
                
                response = {'status': 'success',
                            'response': 'Objekt oprettet'}
            else:
                logger.info('%s not created' % class_name.__name__)
                context = {'form': form,
                           'object_type': class_name.verbose_name}
                response = {'status': 'failure',
                            'response': render_to_string('form.html', RequestContext(request, context))}

        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    obj_id = request.GET.get('id')

    if obj_id:
        obj = get_object_or_404(class_name, id = obj_id)
        form = form_name(instance=obj)
        context = {'form': form,
                   'object_type': obj.verbose_name,
                   'id': obj.id}
    else:
        form = form_name()
        context = {'form': form,
                   'object_type': class_name.verbose_name}

    return render(request, 'form.html', context)

@login_required
def action_form(request, form_name, object_type):
    if request.POST:
        form = form_name(request.POST)
        if form.is_valid():
            obj_dict = form.save()
            response = {'status': 'success',
                        'response': make_message(obj_dict)}
        else:
            print form.errors
            context = {'form': form,
                       'object_type': object_type}
            response = {'status': 'failure',
                        'response': render_to_string('form.html', RequestContext(request, context))}
		
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    form = form_name()
    context = {'form': form, 'object_type': object_type}
    return render(request, 'form.html', context)

@login_required
def action(request, class_name):
    action = request.POST.get('action')
    object_ids = request.POST.get('object_ids')

    if object_ids:
        object_ids = object_ids.split(',')
    else:
        response = {'response': 'Ingen objekter valgt'}
        return HttpResponse(simplejson.dumps(response),
                            content_type='application/json')

    obj_dict = {}

    for object_id in object_ids:
        obj = get_object_or_404(class_name, pk = object_id)
        obj_name = obj.name

        if action == 'loan_single':
            response = obj.loan(request.user)
            try:
                obj_dict[response].append(obj_name)
            except KeyError:
                obj_dict[response] = [obj_name]
        elif action == 'delete':
            if request.user.is_admin:
                obj.delete()
                try:
                    obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS].append(obj_name)
                except KeyError:
                    obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS] = [obj_name]
            else:
                try:
                    obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS].append(obj_name)
                except KeyError:
                    obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS] = [obj_name]
        else:
            action_function = getattr(obj, action)
            response = action_function(request.user)
            try:
                obj_dict[response].append(obj_name)
            except KeyError:
                obj_dict[response] = [obj_name]

    response = {'response': make_message(obj_dict)}

    return HttpResponse(simplejson.dumps(response), 
                        content_type="application/json")

@login_required
def delete(request, class_to_delete):
    object_id = request.POST.get('id')
    logger.warning('%s is trying to delete %s with id %s' % (request.user,
                                                             class_to_delete.__name__,
                                                             object_id))

    if not request.user.is_admin:
        logger.error('%s does not have rights to delete' % (request.user))
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
    if not request.user.is_admin:
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

@login_required
def reservation_delete(request):
    reservation_id = request.GET.get('id')
    logger.warning('%s is trying to delete reservation with id %s' % (request.user, reservation_id))

    if not request.user.is_admin:
        logger.error('Reservation not deleted, user has no rights')
        response = {'response': 'Du har ikke rettigheder til at slette reservationen'}
        return HttpResponse(simplejson.dumps(response), 
                            mimetype="application/json")

    try:
        reservation = get_object_or_404(Reservation, id = reservation_id)
    except Http404:
        logger.error('Reservation not found' % event_id)
        raise Http404

    reservation.delete()
    logger.warning('Reservation deleted')

    response = {'response': 'Reservationen blev slettet'}

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

@login_required
def qr_action(request, pk):
    if request.user.is_authenticated():
        if request.user.is_admin:
            tool = get_object_or_404(Tool, id=pk)
            if tool.location == 'Lager':
                if request.POST:
                    form = QRLoanForm(tool=tool, data=request.POST)
                    if form.is_valid():
                        obj_dict = form.save()
                        context = {'message': make_message(obj_dict)}

                        if MESSAGES.TOOL_LOAN_SUCCESS in obj_dict:
                            context['status'] = 'success'
                        else:
                            context['status'] = 'failure'

                        return render(request, 'qr/success.html', context)
                else:
                    form = QRLoanForm(tool=tool)
            
                context = {'form': form}
                return render(request, 'qr/form.html', context)

            elif tool.location == 'Udlånt' or tool.location == 'Reparation':
                tool.end_loan(request.user)
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
                    tool.end_loan(request.user)
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

@login_required
def inline_form(request, form_name, object_type):
    if request.POST:
        form = form_name(request.POST)
        if form.is_valid():
            obj = form.save()
            response = {'status': 'success',
                        'response': 'Objekt oprettet',
                        'value': obj.id,
                        'name': obj.name}
        else:
            context = {'form': form,
                       'object_type': object_type}
            response = {'status': 'failure',
                        'response': render_to_string('inline_form.html', 
                                                     RequestContext(request, context))}

        return HttpResponse(simplejson.dumps(response), 
                            mimetype='application/json')

    context_dictionary = {'form': form_name(),
                          'object_type': object_type}
    return render(request, 'inline_form.html', context_dictionary)

@login_required
def create_many_tools_form(request):
    if request.POST:
        form = CreateManyToolsForm(request.POST)
        if form.is_valid():
            form.save()
            response = {'status': 'success',
                        'response': 'Værktøj oprettet'}
        else:
            context = {'form': form,
                       'object_type': 'add_many_tools'}
            response = {'status': 'failure',
                        'response': render_to_string('form.html', RequestContext(request, context))}

        return HttpResponse(simplejson.dumps(response), 
                            mimetype='application/json')

    context_dictionary = {'form': CreateManyToolsForm(),
                          'object_type': 'add_many_tools'}
    return render(request, 'form.html', context_dictionary)

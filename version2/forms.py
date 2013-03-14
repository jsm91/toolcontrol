# -*- coding:utf-8 -*-
import datetime

from django import forms
from django.shortcuts import get_object_or_404

from toolcontrol.enums import MESSAGES
from toolcontrol.utils import make_message
from tools.models import ConstructionSite, Container, Employee, Event, Tool
from tools.models import ToolCategory, ToolModel

class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        exclude = ['location','employee','construction_site','end_date']

class ToolModelForm(forms.ModelForm):
    class Meta:
        model = ToolModel

class ToolCategoryForm(forms.ModelForm):
    class Meta:
        model = ToolCategory
        exclude = ['customer',]

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ['customer', 'password', 'last_login', 'is_active', 
                   'loan_threshold', 'receive_sms', 'receive_mail']

    def clean(self):
        cleaned_data = super(EmployeeForm, self).clean()
        phone_number = cleaned_data.get('phone_number')
        email = cleaned_data.get('email')

        if not phone_number and not email:
            raise forms.ValidationError('Enten email eller telefonnummer er påkrævet')

        return cleaned_data

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ['customer', 'password', 'last_login', 'is_active',
                   'is_loan_flagged', 'is_admin', 'name']

    def clean(self):
        cleaned_data = super(SettingsForm, self).clean()
        phone_number = cleaned_data.get('phone_number')
        email = cleaned_data.get('email')

        if not phone_number and not email:
            raise forms.ValidationError('Enten email eller telefonnummer er påkrævet')

        return cleaned_data

class BuildingSiteForm(forms.ModelForm):
    class Meta:
        model = ConstructionSite
        exclude = ['customer', 'is_active']

class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        exclude = ['customer', 'location']

class ActionForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user, action_function_name, model):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for obj_id in self.cleaned_data.get('objects').split(','):
                obj = get_object_or_404(model, id = obj_id)

                if action_function_name == 'delete':
                    name = obj.name
                    if user.is_admin:
                        obj.delete()
                        try:
                            obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS].append(name)
                        except KeyError:
                            obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS] = [name]
                    else:
                        try:
                            obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS].append(name)
                        except KeyError:
                            obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS] = [name]

                else:
                    action_function = getattr(obj, action_function_name)
                    response = action_function(user)

                    try:
                        obj_dict[response].append(obj.name)
                    except KeyError:
                        obj_dict[response] = [obj.name]

        return make_message(obj_dict)

class ReturnToolsForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, id = tool_id)
                response = tool.end_loan(user)

                try:
                    obj_dict[response].append(tool.name)
                except KeyError:
                    obj_dict[response] = [tool.name]

        return make_message(obj_dict)

class LoanToolsForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(),
                                      required=False, label="Medarbejder")
    building_site = forms.ModelChoiceField(queryset=
                                           ConstructionSite.objects.all(),
                                           required=False, label="Byggeplads")

    def __init__(self, user, *args, **kwargs):
        super(LoanToolsForm, self).__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(customer=user.customer)
        self.fields['building_site'].queryset = ConstructionSite.objects.filter(customer=user.customer)

    def clean(self):
        cleaned_data = super(LoanToolsForm, self).clean()
        employee = cleaned_data.get('employee')
        building_site = cleaned_data.get('building_site')

        if not(employee or building_site):
            raise forms.ValidationError('Enten medarbejder eller byggeplads er påkrævet')

        return cleaned_data

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, id = tool_id)
                response = tool.loan(self.cleaned_data.get('employee'), 
                                     self.cleaned_data.get('building_site'))
                
                try:
                    obj_dict[response].append(tool.name)
                except KeyError:
                    obj_dict[response] = [tool.name]

        return make_message(obj_dict)

class LoanToolsSingleForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, id = tool_id)
                response = tool.loan(employee = user)
                
                try:
                    obj_dict[response].append(tool.name)
                except KeyError:
                    obj_dict[response] = [tool.name]

        return make_message(obj_dict)

class ReserveToolsSingleForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)
    start_date = forms.DateField(label='Startdato')
    end_date = forms.DateField(label='Slutdato')

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, id = tool_id)
                response = tool.reserve(employee = user, construction_site=None, start_date = self.cleaned_data.get('start_date'), end_date = self.cleaned_data.get('end_date'))

                
                try:
                    obj_dict[response].append(tool.name)
                except KeyError:
                    obj_dict[response] = [tool.name]

        return make_message(obj_dict)

class ReserveForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(),
                                      required=False, label="Medarbejder")
    building_site = forms.ModelChoiceField(queryset=
                                           ConstructionSite.objects.all(),
                                           required=False, label="Byggeplads")
    start_date = forms.DateField(label="Startdato")
    end_date = forms.DateField(label="Slutdato")

    def __init__(self, user, *args, **kwargs):
        super(ReserveForm, self).__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(customer=user.customer)
        self.fields['building_site'].queryset = ConstructionSite.objects.filter(customer=user.customer)

    def clean(self):
        cleaned_data = super(ReserveForm, self).clean()
        employee = cleaned_data.get('employee')
        building_site = cleaned_data.get('building_site')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if not(employee or building_site):
            raise forms.ValidationError('Enten medarbejder eller byggeplads er påkrævet')

        if end_date < start_date:
            raise forms.ValidationError('Startdato skal være før slutdato')

        return cleaned_data

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, id = tool_id)
                response = tool.reserve(self.cleaned_data.get('employee'), 
                                        self.cleaned_data.get('building_site'),
                                        self.cleaned_data.get('start_date'),
                                        self.cleaned_data.get('end_date'))
                
                try:
                    obj_dict[response].append(tool.name)
                except KeyError:
                    obj_dict[response] = [tool.name]

        return make_message(obj_dict)

class DeleteToolsForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, pk=tool_id)
                tool_name = tool.name 
                if user.is_admin:
                    tool.delete()
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS].append(tool_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS] = [tool_name]
                else:
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS].append(tool_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS] = [tool_name]

        return make_message(obj_dict)

class DeleteToolModelsForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for tool_model_id in self.cleaned_data.get('objects').split(','):
                tool_model = get_object_or_404(ToolModel, pk=tool_model_id)
                tool_model_name = tool_model.name 
                if user.is_admin:
                    tool_model.delete()
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS].append(tool_model_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS] = [tool_model_name]
                else:
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS].append(tool_model_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS] = [tool_model_name]

        return make_message(obj_dict)

class DeleteToolCategoriesForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for tool_category_id in self.cleaned_data.get('objects').split(','):
                tool_category = get_object_or_404(ToolCategory, pk=tool_category_id)
                tool_category_name = tool_category.name 
                if user.is_admin:
                    tool_category.delete()
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS].append(tool_category_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS] = [tool_category_name]
                else:
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS].append(tool_category_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS] = [tool_category_name]

        return make_message(obj_dict)

class DeleteEmployeesForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for employee_id in self.cleaned_data.get('objects').split(','):
                employee = get_object_or_404(Employee, pk=employee_id)
                employee_name = employee.name 
                if user.is_admin:
                    employee.delete()
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS].append(employee_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS] = [employee_name]
                else:
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS].append(employee_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS] = [employee_name]

        return make_message(obj_dict)

class DeleteBuildingSitesForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for building_site_id in self.cleaned_data.get('objects').split(','):
                building_site = get_object_or_404(ConstructionSite, pk=building_site_id)
                building_site_name = building_site.name 
                if user.is_admin:
                    building_site.delete()
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS].append(building_site_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS] = [building_site_name]
                else:
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS].append(building_site_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS] = [building_site_name]

        return make_message(obj_dict)

class DeleteContainersForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for container_id in self.cleaned_data.get('objects').split(','):
                container = get_object_or_404(Container, pk=container_id)
                container_name = container.name 
                if user.is_admin:
                    container.delete()
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS].append(container_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_SUCCESS] = [container_name]
                else:
                    try:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS].append(container_name)
                    except KeyError:
                        obj_dict[MESSAGES.OBJECT_DELETE_RIGHTS] = [container_name]

        return make_message(obj_dict)

class LoanContainersForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)
    building_site = forms.ModelChoiceField(queryset=
                                           ConstructionSite.objects.all(),
                                           label="Byggeplads")

    def __init__(self, user, *args, **kwargs):
        super(LoanContainersForm, self).__init__(*args, **kwargs)
        self.fields['building_site'].queryset = ConstructionSite.objects.filter(customer=user.customer)

    def save(self, user):
        obj_dict = {}
        if self.cleaned_data.get('objects'):
            for container_id in self.cleaned_data.get('objects').split(','):
                container = get_object_or_404(Container, id = container_id)
                response = container.loan(self.cleaned_data.get('building_site'), user)
                
                try:
                    obj_dict[response].append(container.name)
                except KeyError:
                    obj_dict[response] = [container.name]

        return make_message(obj_dict)

class CreateManyToolsForm(forms.Form):
    prefix = forms.CharField(label="Præfiks", 
                             help_text="Præfiks der deles af alt værktøjet")
    start_index = forms.CharField(label="Startindeks", 
                                  help_text="Laveste indeksnummer med foranstillede nuller")
    end_index = forms.IntegerField(label="Slutindeks", 
                                   help_text="Højeste indeksnummer")
    model = forms.ModelChoiceField(queryset=ToolModel.objects.all())
    container = forms.ModelChoiceField(queryset=Container.objects.filter(is_active=True), required=False)
    service_interval = forms.IntegerField(label="Serviceinterval", 
                                          required=False,
                                          help_text = 'Antal måneder mellem service for denne slags værktøj')
    price = forms.IntegerField(label="Pris", required=False)
    invoice_number = forms.IntegerField(label = "Bilagsnummer", 
                                        required = False)
    secondary_name = forms.CharField(label = "Sekundært navn", 
                                     required = False)

    buy_date = forms.DateField(label = "Indkøbsdato")

    def __init__(self, customer, *args, **kwargs):
        super(CreateManyToolsForm, self).__init__(*args, **kwargs)
        self.fields['model'].queryset = ToolModel.objects.filter(category__customer=customer).order_by('name')
        self.fields['buy_date'].initial = datetime.datetime.now()

    def save(self, force_insert=False, force_update=False, commit=True):
        zeros = len(self.cleaned_data['start_index']) - 1
        if not self.cleaned_data['price']:
            price = self.cleaned_data['model'].price
            service_interval = self.cleaned_data['model'].service_interval
        else:
            price = self.cleaned_data['price']
            service_interval = self.cleaned_data['service_interval']
        for n in range(int(self.cleaned_data['start_index']),
                       self.cleaned_data['end_index']+1):
            name = (self.cleaned_data['prefix'] + 
                    self.get_zeros(n, zeros) + str(n))
            tool = Tool(name = name, 
                        price = price, 
                        service_interval = service_interval,
                        model = self.cleaned_data['model'],
                        invoice_number = self.cleaned_data['invoice_number'],
                        secondary_name = self.cleaned_data['secondary_name'],
                        buy_date = self.cleaned_data['buy_date'],
                        container = self.cleaned_data['container'])
            tool.save()
            event = Event(event_type = "Oprettelse", tool = tool)
            event.save()

    def get_zeros(self, n, zeros):
        while n > 9:
            zeros -= 1
            n = n / 10
        out = ""
        for n in range(zeros):
            out += "0"
        return out

    def clean_start_index(self):
        data = self.cleaned_data['start_index']
        try:
            int(data)
        except ValueError:
            raise forms.ValidationError('Start-indekset skal være et tal')
        return data

    def clean(self):
        cleaned_data = super(CreateManyToolsForm, self).clean()
        start_index = cleaned_data.get("start_index")
        end_index = cleaned_data.get("end_index")

        if start_index is not None:
            if int(start_index) > end_index:
                raise forms.ValidationError('Start-indeks skal være lavere end slut-indeks')

        return cleaned_data

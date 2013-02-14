# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django import forms
from django.shortcuts import get_object_or_404

from tools.models import Container, ContainerLoan, ConstructionSite, Employee
from tools.models import Event, ForgotPasswordToken, Reservation, Tool
from tools.models import ToolCategory, ToolModel

class NewForm(forms.Form):
    def as_new_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row = '<tr%(html_class_attr)s><th>%(label)s %(help_text)s</th><td>%(errors)s %(field)s</td></tr>',
            error_row = '<tr><td colspan="2">%s</td></tr>',
            row_ender = '</td></tr>',
            help_text_html = '<img src="/static/Icon_Info.svg" title="%s">',
            errors_on_separate_row = False)

class NewModelForm(forms.ModelForm):
    def as_new_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row = '<tr%(html_class_attr)s><th>%(label)s %(help_text)s %(errors)s</th><td>%(field)s</td></tr>',
            error_row = '<tr><td colspan="2">%s</td></tr>',
            row_ender = '</td></tr>',
            help_text_html = '<img src="/static/Icon_Info.svg" title="%s">',
            errors_on_separate_row = False)
    
class LoanForm(NewModelForm):
    tools = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Event
        fields = ['employee', 'construction_site',]

    def __init__(self, *args, **kwargs):
        super(LoanForm, self).__init__(*args, **kwargs)
        self.fields['employee'].empty_label = 'Vælg medarbejder...'
        self.fields['construction_site'].empty_label = 'Vælg byggeplads...'

    def clean(self):
        cleaned_data = super(LoanForm, self).clean()

        employee = cleaned_data.get('employee')
        construction_site = cleaned_data.get('construction_site')

        if not(employee or construction_site):
        	raise forms.ValidationError('Enten medarbejder eller byggeplads er påkrævet')

        return cleaned_data

    def save(self, commit=True):
        cd = self.cleaned_data
        tool_ids = cd['tools'].split(',')

        obj_dict = {}

        if not self.cleaned_data['tools']:
            return obj_dict

        for tool_id in tool_ids:
            tool = get_object_or_404(Tool, id = tool_id)
            response = tool.loan(cd['employee'], cd['construction_site'])
            try:
                obj_dict[response].append(tool.name)
            except KeyError:
                obj_dict[response] = [tool.name]

        return obj_dict

class QRLoanForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['employee', 'construction_site',]

    def __init__(self, tool, *args, **kwargs):
        super(QRLoanForm, self).__init__(*args, **kwargs)
        self.tool = tool
        self.fields['employee'].empty_label = 'Vælg medarbejder...'
        self.fields['construction_site'].empty_label = 'Vælg byggeplads...'

    def clean(self):
        cleaned_data = super(QRLoanForm, self).clean()

        employee = cleaned_data.get('employee')
        construction_site = cleaned_data.get('construction_site')

        if not(employee or construction_site):
        	raise forms.ValidationError('Enten medarbejder eller byggeplads er påkrævet')

        return cleaned_data

    def save(self, commit=True):
        cd = self.cleaned_data
        self.tool.loan(cd['employee'], cd['construction_site'])

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

    def save(self, commit=True):
        email = self.cleaned_data.get('email')
        for user in Employee.objects.filter(email=email):
            token = Employee.objects.make_random_password()

            forgot_password_token = ForgotPasswordToken(token=token, user=user)
            forgot_password_token.save()

            message = ('Hej ' + user.name + '\n\n' +
                       'Vi har fået en anmodning om at nulstille dit kodeord.'+
                       'Hvis du ønsker at nulstille dit kodeord, bedes du '+
                       'tilgå denne URL: '+
                       'http://skou.toolcontrol.dk/reset_password/' +token+
                       '. Hvis du ikke har bedt om at få nulstillet '+
                       'dit kodeord, kan du se bort fra denne mail\n\n'+
                       'MVH\nToolControl for Skou Gruppen A/S')

            user.send_mail('Nulstilling af kodeord', message)

    def clean(self):
        cleaned_data = super(ForgotPasswordForm, self).clean()
        email = cleaned_data.get('email')

        user = Employee.objects.filter(email=email)[0]

        if user is None:
            raise forms.ValidationError('Ingen bruger med den angivne email')

        return cleaned_data
        

class ToolCategoryForm(NewModelForm):
    class Meta:
        model = ToolCategory
        fields = ['name',]

class ToolModelForm(NewModelForm):
    category = forms.ModelChoiceField(queryset=ToolCategory.objects.all().order_by('name'),
                                      empty_label=None,
                                      label='Kategori')

    def __init__(self, *args, **kwargs):
        super(ToolModelForm, self).__init__(*args, **kwargs)
        self.fields['service_interval'].help_text = 'Antal måneder mellem service. 0 angiver at værktøj af denne model ikke skal serviceres'


    class Meta:
        model = ToolModel
        exclude = ['number_of_tools', 'total_price']

class ContainerForm(NewModelForm):
    class Meta:
        model = Container
        exclude = ['location',]

class ContainerLoanForm(NewModelForm):
    containers = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = ContainerLoan
        fields = ['construction_site',]

    def save(self, commit=True):
        cd = self.cleaned_data
        container_ids = cd['containers'].split(',')

        obj_dict = {}

        if not self.cleaned_data['containers']:
            return obj_dict

        for container_id in container_ids:
            container = get_object_or_404(Container, id = container_id)
            response = container.loan(cd['construction_site'])

            try:
                obj_dict[response].append(container.name)
            except KeyError:
                obj_dict[response] = [container.name]

        return obj_dict

class ToolForm(NewModelForm):
    model = forms.ModelChoiceField(queryset=ToolModel.objects.all().order_by('name'),
                                   empty_label=None,
                                   label='Model')

    def __init__(self, *args, **kwargs):
        super(ToolForm, self).__init__(*args, **kwargs)
        self.fields['buy_date'].initial = datetime.datetime.now()
        try:
            self.fields['model'].initial = ToolModel.objects.all()[0]
        except:
            pass
        if self.fields['model'].initial:
            self.fields['price'].initial = self.fields['model'].initial.price
            self.fields['service_interval'].initial = self.fields['model'].initial.service_interval
        self.fields['service_interval'].help_text = 'Antal måneder mellem service. 0 angiver at værktøjet ikke skal serviceres'
    class Meta:
        model = Tool
        exclude = ['location','employee','construction_site','end_date']

class EmployeeForm(NewModelForm):
    class Meta:
        model = Employee
        exclude = ['password', 'last_login', 'is_loan_flagged', 'is_employee',
                   'sms_loan_threshold', 'email_loan_threshold',]

    def clean(self):
        cleaned_data = super(EmployeeForm, self).clean()
        phone_number = cleaned_data.get('phone_number')
        email = cleaned_data.get('email')

        if not phone_number and not email:
            raise forms.ValidationError('Enten email eller telefonnummer er påkfrævet')

        return cleaned_data

    def save(self, commit=True):
        employee = super(EmployeeForm, self).save(commit=False)

        if not employee.pk:
            password = Employee.objects.make_random_password()
            employee.set_password(password)
            
            message = ('Hej ' + employee.name + '\n\n' + 
                       'Du er netop blevet oprettet i ToolControl-systemet ' +
                       'hos Skou Gruppen A/S. Du kan logge ind med navnet ' +
                       employee.name + ' samt kodeordet ' + password + '. ' +
                       'Kodeordet kan ændres når du er logget ind.\n\n' +
                       'MVH\n' +
                       'ToolControl')

            employee.send_mail('Oprettet som bruger', message)
            employee.send_sms(message)

        if commit:
            employee.save()
        return employee
    
class BuildingSiteForm(NewModelForm):
    class Meta:
        model = ConstructionSite

    def save(self, commit=True):
        building_site = super(BuildingSiteForm, self).save(commit=False)
        if commit:
            building_site.save()
        return building_site

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['sms_loan_threshold', 'email_loan_threshold',
                  'email', 'phone_number',]

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        if not kwargs['instance'].is_admin:
            self.fields['sms_loan_threshold'].widget.attrs['disabled'] = 'disabled'
            self.fields['email_loan_threshold'].widget.attrs['disabled'] = 'disabled'

        self.fields['sms_loan_threshold'].required = False
        self.fields['email_loan_threshold'].required = False

class CreateManyToolsForm(NewForm):
    prefix = forms.CharField(label="Præfiks", 
                             help_text="Præfiks der deles af alt værktøjet")
    start_index = forms.CharField(label="Startindeks", 
                                  help_text="Laveste indeksnummer med foranstillede nuller")
    end_index = forms.IntegerField(label="Slutindeks", 
                                   help_text="Højeste indeksnummer")
    model = forms.ModelChoiceField(queryset=ToolModel.objects.all(), 
                                   empty_label=None)
    container = forms.ModelChoiceField(queryset=Container.objects.filter(is_active=True), required=False)
    service_interval = forms.IntegerField(label="Serviceinterval", 
                                          required=False,
                                          help_text = 'Antal måneder mellem service for denne slags værktøj')
    price = forms.IntegerField(label="Pris", required=False)
    invoice_number = forms.IntegerField(label = "Bilagsnummer", 
                                        required = False)
    secondary_name = forms.CharField(label = "Sekundært navn", 
                                     required = False)

    buy_date = forms.DateTimeField(label = "Indkøbsdato")

    def __init__(self, *args, **kwargs):
        super(CreateManyToolsForm, self).__init__(*args, **kwargs)
        self.fields['buy_date'].initial = datetime.datetime.now()
        try:
            self.fields['model'].initial = ToolModel.objects.all()[0]
        except:
            pass
        if self.fields['model'].initial:
            self.fields['price'].initial = self.fields['model'].initial.price
            self.fields['service_interval'].initial = self.fields['model'].initial.service_interval

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

class ReservationForm(NewModelForm):
    tools = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Reservation
        exclude = ['tool']

    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].initial = datetime.datetime.now()
        self.fields['end_date'].initial = (datetime.datetime.now() + 
                                           datetime.timedelta(days=7))

    def save(self, commit=True):
        tool_ids = self.cleaned_data['tools'].split(',')

        obj_dict = {}

        if not self.cleaned_data['tools']:
            return obj_dict

        for tool_id in tool_ids:
            tool = get_object_or_404(Tool, id = tool_id)
            response = tool.reserve(employee = self.cleaned_data['employee'],
                                    construction_site = self.cleaned_data['construction_site'],
                                    start_date = self.cleaned_data['start_date'],
                                    end_date = self.cleaned_data['end_date'])

            try:
                obj_dict[response].append(tool.name)
            except KeyError:
                obj_dict[response] = [tool.name]

        return obj_dict

    def clean(self):
        cleaned_data = super(ReservationForm, self).clean()

        if self.cleaned_data['end_date'] < self.cleaned_data['start_date']:
            raise forms.ValidationError('Slutdato skal være efter startdato')

        if (not self.cleaned_data['employee'] and 
            not self.cleaned_data['construction_site']):
            raise forms.ValidationError('Der skal vælges enten en medarbejder eller en byggeplads')
        
        return cleaned_data

# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django import forms

from tools.models import Event, ForgotPasswordToken, Loaner, Tool
from tools.models import ToolCategory, ToolModel

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

    def save(self, commit=True):
        email = self.cleaned_data.get('email')
        user = Loaner.objects.filter(email=email)[0]
        token = Loaner.objects.make_random_password()

        forgot_password_token = ForgotPasswordToken(token=token, user=user)
        forgot_password_token.save()

        message = "Hej " + user.name + "<br><br>"
        message += "Vi har fået en anmodning om at nulstille dit kodeord."
        message += 'Hvis du ønsker at nulstille dit kodeord, bedes du tilgå '
        message += 'denne URL: http://toolbase.rmbsupport.dk/reset_password/'
        message += token + '. Hvis du ikke har bedt om at få nulstillet '
        message += 'dit kodeord, kan du se bort fra denne mail<br><br>'
        message += 'MVH<br>'
        message += 'ToolBase for SkouGruppen A/S'

        user.send_mail('Nulstilling af kodeord', message)

        return forgot_password_token

    def clean(self):
        cleaned_data = super(ForgotPasswordForm, self).clean()
        email = cleaned_data.get('email')

        user = Loaner.objects.filter(email=email)[0]

        if user is None:
            raise forms.ValidationError('Ingen bruger med den angivne email')

        return cleaned_data
        

class ToolCategoryForm(forms.ModelForm):
    class Meta:
        model = ToolCategory
        fields = ['name',]

class ToolModelForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=ToolCategory.objects.all(),
                                      empty_label=None,
                                      label='Kategori')

    class Meta:
        model = ToolModel
        exclude = ['number_of_tools', 'total_price']

class ToolForm(forms.ModelForm):
    model = forms.ModelChoiceField(queryset=ToolModel.objects.all(),
                                   empty_label=None,
                                   label='Model')

    def __init__(self, *args, **kwargs):
        super(ToolForm, self).__init__(*args, **kwargs)
        try:
            self.fields['model'].initial = ToolModel.objects.all()[0]
        except:
            pass

        if self.fields['model'].initial:
            self.fields['price'].initial = self.fields['model'].initial.price
            self.fields['service_interval'].initial = self.fields['model'].initial.service_interval

    class Meta:
        model = Tool
        exclude = ['location','loaned_to']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Loaner
        exclude = ['password', 'last_login', 'is_loan_flagged', 'is_employee',
                   'sms_loan_threshold', 'email_loan_threshold',]

    def save(self, commit=True):
        employee = super(EmployeeForm, self).save(commit=False)

        if not employee.pk:
            password = Loaner.objects.make_random_password()
            employee.set_password(password)
            
            message = ('Hej ' + employee.name + '\n' + 
                       'Du er netop blevet oprettet i ToolBase-systemet ' +
                       'hos Skou Gruppen A/S. Du kan logge ind med navnet ' +
                       employee.name + ' samt kodeordet ' + password + '. ' +
                       'Kodeordet kan ændres når du er logget ind.\n\n' +
                       'MVH\n' +
                       'Skou Gruppen A/S')

            employee.send_mail('Oprettet som bruger', message)
            employee.send_sms(message)

            print password

        if commit:
            employee.save()
        return employee
    

class BuildingSiteForm(forms.ModelForm):
    class Meta:
        model = Loaner
        fields = ['name', 'is_active']

    def save(self, commit=True):
        building_site = super(BuildingSiteForm, self).save(commit=False)
        building_site.is_employee = False
        if commit:
            building_site.save()
        return building_site

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Loaner
        fields = ['sms_loan_threshold', 'email_loan_threshold',
                  'email', 'phone_number',]

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        if not kwargs['instance'].is_tool_admin:
            self.fields['sms_loan_threshold'].widget.attrs['disabled'] = 'disabled'
            self.fields['email_loan_threshold'].widget.attrs['disabled'] = 'disabled'

        self.fields['sms_loan_threshold'].required = False
        self.fields['email_loan_threshold'].required = False

class CreateManyToolsForm(forms.Form):
    prefix = forms.CharField(label="Præfiks", 
                             help_text="Præfiks der deles af alt værktøjet")
    start_index = forms.CharField(label="Startindeks", 
                                  help_text="Laveste indeksnummer med foranstillede nuller.")
    end_index = forms.IntegerField(label="Slutindeks", 
                                   help_text="Højeste indeksnummer")
    model = forms.ModelChoiceField(queryset=ToolModel.objects.all(), 
                                   empty_label=None)
    service_interval = forms.IntegerField(label="Serviceinterval", 
                                          required=False)
    price = forms.IntegerField(label="Pris", required=False)
    invoice_number = forms.IntegerField(label = "Bilagsnummer", 
                                        required = False)
    secondary_name = forms.CharField(label = "Sekundært navn", 
                                     required = False)

    def __init__(self, *args, **kwargs):
        super(CreateManyToolsForm, self).__init__(*args, **kwargs)
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
            price = self.cleaned_data['model'].service_interval
        else:
            price = self.cleaned_data['price']
            price = self.cleaned_data['service_interval']
        for n in range(int(self.cleaned_data['start_index']),
                       self.cleaned_data['end_index']+1):
            name = (self.cleaned_data['prefix'] + 
                    self.get_zeros(n, zeros) + str(n))
            tool = Tool(name = name, price = price, 
                        service_interval = service_interval,
                        model = self.cleaned_data['model'],
                        invoice_number = self.cleaned_data['invoice_number'],
                        secondary_name = self.cleaned_data['secondary_name'])
            tool.save()
            event = Event(event_type = "Oprettelse", tool = tool)
            event.save()
        number_of_tools = (self.cleaned_data['end_index'] + 
                           1 - int(self.cleaned_data['start_index']))
        model = self.cleaned_data['model']
        model.number_of_tools += number_of_tools
        model.total_price += (number_of_tools * price)
        model.save()
        model.category.number_of_tools += number_of_tools
        model.category.total_price += (number_of_tools * price)
        model.category.save()

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

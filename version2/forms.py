# -*- coding:utf-8 -*-
from django import forms
from django.shortcuts import get_object_or_404

from tools.models import ConstructionSite, Container, Employee, Tool
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


class BuildingSiteForm(forms.ModelForm):
    class Meta:
        model = ConstructionSite
        exclude = ['customer', 'is_active']

class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        exclude = ['customer', 'location', 'is_active']

class ServiceForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, pk=tool_id)
                tool.service(user)

class LoanForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(),
                                      required=False, label="Medarbejder")
    building_site = forms.ModelChoiceField(queryset=
                                           ConstructionSite.objects.all(),
                                           required=False, label="Byggeplads")

    def clean(self):
        cleaned_data = super(LoanForm, self).clean()
        employee = cleaned_data.get('employee')
        building_site = cleaned_data.get('building_site')

        if not(employee or building_site):
            raise forms.ValidationError('Enten medarbejder eller byggeplads er påkrævet')

        return cleaned_data

    def save(self, user):
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, pk=tool_id)
                tool.loan(self.cleaned_data.get('employee'), 
                          self.cleaned_data.get('building_site'))

class RepairForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, pk=tool_id)
                tool.repair(user)

class ReturnForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, pk=tool_id)
                tool.end_loan(user)

class ReserveForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(),
                                      required=False, label="Medarbejder")
    building_site = forms.ModelChoiceField(queryset=
                                           ConstructionSite.objects.all(),
                                           required=False, label="Byggeplads")
    start_date = forms.DateField(label="Startdato")
    end_date = forms.DateField(label="Slutdato")

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
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, pk=tool_id)
                tool.reserve(self.cleaned_data.get('employee'), 
                             self.cleaned_data.get('building_site'),
                             self.cleaned_data.get('start_date'),
                             self.cleaned_data.get('end_date'))

class ScrapForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, pk=tool_id)
                tool.scrap(user)

class LostForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, pk=tool_id)
                tool.lost(user)

class DeleteToolsForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        if self.cleaned_data.get('objects'):
            for tool_id in self.cleaned_data.get('objects').split(','):
                tool = get_object_or_404(Tool, pk=tool_id)
                tool.delete()

class DeleteToolModelsForm(forms.Form):
    objects = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, user):
        if self.cleaned_data.get('objects'):
            for tool_model_id in self.cleaned_data.get('objects').split(','):
                tool_model = get_object_or_404(ToolModel, pk=tool_model_id)
                tool_model.delete()

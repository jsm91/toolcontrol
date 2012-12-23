# -*- coding:utf-8 -*-
import urllib

from django.contrib.auth.models import BaseEmployeeManager, AbstractBaseEmployee
from django.core.mail import send_mail
from django.db import models

class EmployeeManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number,
                    password=None):
        if not email:
            raise ValueError("Medarbejdere skal have en email-adresse")

        employee = self.model(
            email=EmployeeManager.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number)
        
        employee.set_password(password)
        employee.save(using=self._db)
        return employee

    def create_superuser(self, email, first_name, last_name, phone_number,
                         password):
        employee = self.create_employee(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password)
        employee.is_office_admin = True
        employee.save(using=self._db)
        return employee
    
class Employee(AbstractBaseEmployee):
    email = models.EmailField(
        verbose_name='Email-adresse',
        max_length=255,
        unique=True,
        db_index=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.IntegerField()
    
    is_active = models.BooleanField(default=True)
    is_office_admin = models.BooleanField(default=False)
    is_tool_admin = models.BooleanField(default=False)
    is_loan_flagged = models.BooleanField(default=False)

    tools_num_page = models.IntegerField(default=25)
    events_num_page = models.IntegerField(default=25)
    models_num_page = models.IntegerField(default=25)
    categories_num_page = models.IntegerField(default=25)
    loans_num_page = models.IntegerField(default=25)
    employees_num_page = models.IntegerField(default=25)
    
    objects = EmployeeManager()
    
    EMPLOYEENAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    
    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)
    
    def get_short_name(self):
        return self.email
    
    def __unicode__(self):
        return self.email

    def send_mail(self, subject, message):
        send_mail(subject, message, "toolbox@skougruppen.dk", [self.email])

    def send_sms(self, message):
        params = urllib.urlencode({'username': 'hromby', 
                                   'password': 'IRMLVJ',
                                   'recipient': self.phone_number,
                                   'message': message.encode('utf-8'),
                                   'utf8': 1})

        f = urllib.urlopen("http://cpsms.dk/sms?%s" % params)
        content = f.read()
        pattern = re.compile("<(?P<status>.+?)>(?P<message>.+?)</.+?>")
        match = pattern.search(content)
        return match.group('status'), match.group('message')

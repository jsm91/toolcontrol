# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import datetime, re, urllib
from itertools import chain

import logging
logger = logging.getLogger(__name__)

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models import Sum
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from toolcontrol.enums import MESSAGES
from customers.models import Customer

class ConstructionSite(models.Model):
    verbose_name = 'building_site'

    name = models.CharField('Navn', max_length=200)
    is_active = models.BooleanField('Aktiv', default=True)
    customer = models.ForeignKey(Customer, verbose_name='Kunde')

    def make_active(self, user):
        if not user.is_admin:
           return MESSAGES.CONSTRUCTION_SITE_MAKE_ACTIVE_RIGHTS
        
        if self.is_active:
            return MESSAGES.CONSTRUCTION_SITE_MAKE_ACTIVE_ACTIVE
        
        self.is_active = True
        self.save()
        return MESSAGES.CONSTRUCTION_SITE_MAKE_ACTIVE_SUCCESS

    def make_inactive(self, user):
        if not user.is_admin:
            return MESSAGES.CONSTRUCTION_SITE_MAKE_ACTIVE_RIGHTS
        
        if not self.is_active:
            return MESSAGES.CONSTRUCTION_SITE_MAKE_INACTIVE_INACTIVE
        
        self.is_active = False
        self.save()
        return MESSAGES.CONSTRUCTION_SITE_MAKE_INACTIVE_SUCCESS

    def __unicode__(self):
        return self.name

class Container(models.Model):
    verbose_name = 'container'

    name = models.CharField('Navn', max_length=255)
    location = models.ForeignKey(ConstructionSite, null=True, default=None,
                                 verbose_name = 'Placering')
    is_active = models.BooleanField('Aktiv')
    customer = models.ForeignKey(Customer, verbose_name='Kunde')

    def make_active(self, user):
        if not user.is_admin:
           return MESSAGES.CONTAINER_MAKE_ACTIVE_RIGHTS

        if self.is_active:
            return MESSAGES.CONTAINER_MAKE_ACTIVE_ACTIVE
        
        self.is_active = True
        self.save()
        return MESSAGES.CONTAINER_MAKE_ACTIVE_SUCCESS

    def make_inactive(self, user):
        if not user.is_admin:
           return MESSAGES.CONTAINER_MAKE_INACTIVE_RIGHTS

        if not self.is_active:
            return MESSAGES.CONTAINER_MAKE_INACTIVE_INACTIVE
        
        self.is_active = False
        self.save()
        return MESSAGES.CONTAINER_MAKE_INACTIVE_SUCCESS

    def loan(self, construction_site, user):
        if not user.is_admin:
           return MESSAGES.CONTAINER_LOAN_RIGHTS

        if self.location == None:
            container_loan = ContainerLoan(container=self,
                                           construction_site=construction_site)
            container_loan.save()

            for tool in self.tool_set.filter(location='Lager'):
                tool.loan(construction_site=construction_site)

            self.location = construction_site
            self.save()

            return MESSAGES.CONTAINER_LOAN_SUCCESS
        else:
            return MESSAGES.CONTAINER_LOAN_LOAN

    def end_loan(self, user):
        if not user.is_admin:
           return MESSAGES.CONTAINER_RETURN_RIGHTS

        if self.location != None:
            container_loan = self.containerloan_set.filter(end_date__isnull=True)[0]
            container_loan.end_date = datetime.datetime.now()
            container_loan.save()

            for tool in self.tool_set.filter(construction_site=self.location):
                tool.end_loan()

            self.location = None
            self.save()

            return MESSAGES.CONTAINER_RETURN_SUCCESS
        else:
            return MESSAGES.CONTAINER_RETURN_STORE

    def __unicode__(self):
        return self.name

class ContainerLoan(models.Model):
    container = models.ForeignKey(Container)
    construction_site = models.ForeignKey(ConstructionSite)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

class EmployeeManager(BaseUserManager):
    def create_user(self, name, email, phone_number, password=None):
        employee = self.model(name=name, email=email, 
                              phone_number=phone_number)
        
        employee.set_password(password)
        employee.save(using=self._db)
        return employee

    def create_superuser(self, name, email, phone_number, password):
        employee = self.create_employee(name=name, email=email, 
                                        phone_number=phone_number,
                                        password=password)
        employee.is_admin = True
        employee.save(using=self._db)
        return employee

class Employee(AbstractBaseUser):
    verbose_name = 'employee'

    name = models.CharField('Navn', max_length=200, unique=True, db_index=True)
    email = models.EmailField('Email', max_length=255, blank=True)
    phone_number = models.IntegerField('Telefonnummer', blank=True, null=True)
    customer = models.ForeignKey(Customer, verbose_name='Kunde', null=True, blank=True)

    is_active = models.BooleanField('Aktiv', default=True)
    is_admin = models.BooleanField('Administrator', default=False)
    is_loan_flagged = models.BooleanField('Låneflag', default=False)

    # Number of tools needed for sending SMS or email to admin
    loan_threshold = models.IntegerField('Min. udlån ved besked', 
                                         null=True, default=None)

    # Method of communication
    receive_sms = models.BooleanField('Modtag SMS fra systemet', 
                                      default=True)
    receive_mail = models.BooleanField('Modtag mail fra systemet', 
                                       default=True)

    objects = EmployeeManager()
    
    USERNAME_FIELD = 'name'

    def send_message(self, subject, message):
        if self.receive_sms:
            self.send_sms(message)
        if self.receive_mail:
            self.send_mail(subject, message)

    def mark_login(self):
        login = Login(employee=self)
        login.save()
    
    def make_active(self, user):
        if not user.is_admin:
           return MESSAGES.EMPLOYEE_MAKE_ACTIVE_RIGHTS

        if self.is_active:
            return MESSAGES.EMPLOYEE_MAKE_ACTIVE_ACTIVE
        
        self.is_active = True
        self.save()
        return MESSAGES.EMPLOYEE_MAKE_ACTIVE_SUCCESS

    def make_inactive(self, user):
        if not user.is_admin:
           return MESSAGES.EMPLOYEE_MAKE_INACTIVE_RIGHTS

        if not self.is_active:
            return MESSAGES.EMPLOYEE_MAKE_INACTIVE_INACTIVE
        
        self.is_active = False
        self.save()
        return MESSAGES.EMPLOYEE_MAKE_INACTIVE_SUCCESS

    def make_admin(self, user):
        if not user.is_admin:
           return MESSAGES.EMPLOYEE_MAKE_ADMIN_RIGHTS

        if self.is_admin:
            return MESSAGES.EMPLOYEE_MAKE_ADMIN_ADMIN
        
        self.is_admin = True
        self.save()
        return MESSAGES.EMPLOYEE_MAKE_ADMIN_SUCCESS

    def make_not_admin(self, user):
        if not user.is_admin:
           return MESSAGES.EMPLOYEE_REMOVE_ADMIN_RIGHTS

        if not self.is_admin:
            return MESSAGES.EMPLOYEE_REMOVE_ADMIN_ADMIN
        
        self.is_admin = False
        self.save()
        return MESSAGES.EMPLOYEE_REMOVE_ADMIN_SUCCESS

    def make_loan_flagged(self, user):
        if not user.is_admin:
           return MESSAGES.EMPLOYEE_SET_LOAN_FLAG_RIGHTS

        if self.is_loan_flagged:
            return MESSAGES.EMPLOYEE_SET_LOAN_FLAG_FLAGGED
        
        self.is_loan_flagged = True
        self.save()
        return MESSAGES.EMPLOYEE_SET_LOAN_FLAG_SUCCESS

    def make_not_loan_flagged(self, user):
        if not user.is_admin:
           return MESSAGES.EMPLOYEE_REMOVE_LOAN_FLAG_RIGHTS

        if not self.is_loan_flagged:
            return MESSAGES.EMPLOYEE_REMOVE_LOAN_FLAG_FLAGGED
        
        self.is_loan_flagged = False
        self.save()
        return MESSAGES.EMPLOYEE_REMOVE_LOAN_FLAG_SUCCESS

    def send_mail(self, subject, message):
        logger.debug('Sending mail to %s with content %s' % (self.name, message))
        if self.email:
            try:
                send_mail(subject, message, 'ToolControl <kontakt@toolcontrol.dk>', 
                          [self.email])
                logger.debug('Mail successfully sent')
            except Exception, e:
                logger.error('Mail not sent: %s' % e)
        else:
            logger.debug('Mail not sent, user has no email')

    def send_sms(self, message):
        logger.debug('Sending SMS to %s with content %s' % (self.name, message))
        if self.phone_number:
            params = urllib.urlencode({'username': 'hromby', 
                                       'password': 'IRMLVJ',
                                       'recipient': self.phone_number,
                                       'message': message.encode('utf-8'),
                                       'utf8': 1,
                                       'from': 'ToolControl',})

            f = urllib.urlopen("http://cpsms.dk/sms?%s" % params)
            content = f.read()
            pattern = re.compile("<(?P<status>.+?)>(?P<message>.+?)</.+?>")
            match = pattern.search(content)
            
            if match.group('status') == 'succes':
                logger.debug('SMS gateway returned "%s: %s"' % (match.group('status'),
                                                                match.group('message')))
                if self.customer:
                    self.customer.sms_sent += 1
                    self.customer.save()
            else:
                logger.error('SMS gateway returned "%s: %s"' % (match.group('status'),
                                                                match.group('message')))

            return match.group('status'), match.group('message')
        else:
            logger.debug('SMS not sent, user has no phone number')

    def get_finished_loans(self):
        return self.event_set.filter(end_date=None)

class ForgotPasswordToken(models.Model):
    token = models.CharField(max_length=200)
    user = models.ForeignKey(Employee)

class ToolCategory(models.Model):
    verbose_name = 'category'

    name = models.CharField('Navn', max_length=200)
    customer = models.ForeignKey(Customer, verbose_name='Kunde')

    def total_price(self):
        price = Tool.objects.filter(model__category=self).aggregate(Sum('price'))
        if price['price__sum'] is None:
            return 0
        else:
            return price['price__sum']

    def number_of_models(self):
        return ToolModel.objects.filter(category=self).count()

    def number_of_tools(self):
        return Tool.objects.filter(model__category=self).count()

    def __unicode__(self):
        return self.name

class ToolModel(models.Model):
    verbose_name = 'model'

    name = models.CharField('Navn', max_length=200)
    category = models.ForeignKey(ToolCategory)
    service_interval = models.IntegerField('Serviceinterval', default=6)
    price = models.IntegerField('Pris', default=0)

    def total_price(self):
        price = Tool.objects.filter(model=self).aggregate(Sum('price'))
        if price['price__sum'] is None:
            return 0
        else:
            return price['price__sum']

    def number_of_tools(self):
        return Tool.objects.filter(model=self).count()

    def __unicode__(self):
        return self.name

class Tool(models.Model):
    verbose_name = 'tool'

    LOCATION_CHOICES = (
        ('Lager', 'Lager'),
        ('Udlånt', 'Udlånt'),
        ('Reparation', 'Reparation'),
        ('Bortkommet', 'Bortkommet'),
        ('Kasseret', 'Kasseret')
        )
    name = models.CharField('Navn', max_length=200)
    model = models.ForeignKey(ToolModel)
    service_interval = models.IntegerField('Serviceinterval', default=6)
    price = models.IntegerField('Pris', default=0)
    last_service = models.DateTimeField('Seneste service', auto_now_add=True)
    location = models.CharField('Placering', choices=LOCATION_CHOICES, 
                                max_length=20, default="Lager")

    employee = models.ForeignKey(Employee, null=True)
    construction_site = models.ForeignKey(ConstructionSite, null=True)

    container = models.ForeignKey(Container, null=True, blank=True)

    invoice_number = models.IntegerField('Bilagsnummer', null=True, blank=True)
    secondary_name = models.CharField('Sekundært navn', max_length=200, 
                                      null=True, blank=True)

    buy_date = models.DateField('Købsdato', 
                                    default=datetime.datetime.now())
    end_date = models.DateField('Ophørsdato',
                                    null=True, blank=True)

    
    def get_location(self):
        if self.location == 'Udlånt':
            if self.employee and self.construction_site:
                return "%s/%s" % (self.employee, self.construction_site)
            elif self.employee:
                return self.employee
            else:
                return self.construction_site
        else:
            return self.location

    def service(self, user):
        if not user.is_admin:
           return MESSAGES.TOOL_SERVICE_RIGHTS

        if self.location == 'Lager':
            event = Event(event_type='Service', tool=self)
            event.save()
            self.last_service = event.start_date
            self.save()
            return MESSAGES.TOOL_SERVICE_SUCCESS
        elif self.location == 'Udlånt':
            return MESSAGES.TOOL_SERVICE_LOAN
        elif self.location == 'Kasseret':
            return MESSAGES.TOOL_SERVICE_SCRAPPED
        elif self.location == 'Bortkommet':
            return MESSAGES.TOOL_SERVICE_LOST
        elif self.location == 'Reparation':
            return MESSAGES.TOOL_SERVICE_REPAIR

    def scrap(self, user):
        if not user.is_admin:
           return MESSAGES.TOOL_SCRAP_RIGHTS

        if self.location == 'Lager':
            event = Event(event_type='Kasseret', tool=self)
            event.save()
            self.location = 'Kasseret'
            self.end_date = datetime.datetime.now()
            self.save()
            return MESSAGES.TOOL_SCRAP_SUCCESS
        elif self.location == 'Udlånt':
            return MESSAGES.TOOL_SCRAP_LOAN
        elif self.location == 'Kasseret':
            return MESSAGES.TOOL_SCRAP_SCRAPPED
        elif self.location == 'Bortkommet':
            return MESSAGES.TOOL_SCRAP_LOST
        elif self.location == 'Reparation':
            return MESSAGES.TOOL_SCRAP_REPAIR
        else:
            return False

    def lost(self, user):
        if not user.is_admin:
           return MESSAGES.TOOL_LOST_RIGHTS

        if self.location == 'Lager':
            event = Event(event_type='Bortkommet', tool=self)
            event.save()
            self.location = 'Bortkommet'
            self.end_date = datetime.datetime.now()
            self.save()
            return MESSAGES.TOOL_LOST_SUCCESS
        elif self.location == 'Udlånt':
            return MESSAGES.TOOL_LOST_LOAN
        elif self.location == 'Kasseret':
            return MESSAGES.TOOL_LOST_SCRAPPED
        elif self.location == 'Bortkommet':
            return MESSAGES.TOOL_LOST_LOST
        elif self.location == 'Reparation':
            return MESSAGES.TOOL_LOST_REPAIR
        else:
            return False

    def loan(self, employee=None, construction_site=None):
        if not(employee or construction_site):
            return MESSAGES.TOOL_LOAN_FAILURE

        reservations = self.is_reserved(datetime.datetime.now())

        # Check for reservation
        if reservations:
            reservation = reservations[0]
            if (employee != reservation.employee and
                construction_site != reservation.construction_site):
                return MESSAGES.TOOL_LOAN_RESERVED

        if self.location == 'Lager':
            event = Event(event_type='Udlån', tool=self,
                          employee=employee, 
                          construction_site=construction_site)
            event.save()
            self.location = 'Udlånt'
            self.employee = employee
            self.construction_site = construction_site
            self.save()
            return MESSAGES.TOOL_LOAN_SUCCESS
        elif self.location == 'Udlånt':
            return MESSAGES.TOOL_LOAN_LOAN
        elif self.location == 'Kasseret':
            return MESSAGES.TOOL_LOAN_SCRAPPED
        elif self.location == 'Bortkommet':
            return MESSAGES.TOOL_LOAN_LOST
        elif self.location == 'Reparation':
            return MESSAGES.TOOL_LOAN_REPAIR
        else:
            return False

    def repair(self, user):
        if not user.is_admin:
           return MESSAGES.TOOL_REPAIR_RIGHTS

        if self.location == 'Lager':
            event = Event(event_type='Reparation', tool=self)
            event.save()
            self.location = 'Reparation'
            self.save()
            return MESSAGES.TOOL_REPAIR_SUCCESS
        elif self.location == 'Udlånt':
            return MESSAGES.TOOL_REPAIR_LOAN
        elif self.location == 'Kasseret':
            return MESSAGES.TOOL_REPAIR_SCRAPPED
        elif self.location == 'Bortkommet':
            return MESSAGES.TOOL_REPAIR_LOST
        elif self.location == 'Reparation':
            return MESSAGES.TOOL_REPAIR_REPAIR
        else:
            return False

    def end_loan(self, user):
        if not user.is_admin and self.employee != user:
           return MESSAGES.TOOL_RETURN_RIGHTS

        if self.location == 'Udlånt' or self.location == 'Reparation':
            event = self.get_last_event()
            event.end()
            return MESSAGES.TOOL_RETURN_SUCCESS
        elif self.location == 'Kasseret':
            return MESSAGES.TOOL_RETURN_SCRAPPED
        elif self.location == 'Bortkommet':
            return MESSAGES.TOOL_RETURN_LOST
        elif self.location == 'Lager':
            return MESSAGES.TOOL_RETURN_STORE
        else:
            return False

    def get_last_event(self):
        return self.event_set.all().order_by('-start_date')[0]

    def update_last_service(self):
        logger.info('Updating last service for %s' % self.name)
        try:
            last_service = self.event_set.filter(event_type='Service').order_by('-start_date')[0]
            logger.info('Last service is a service event at %s' % last_service.start_date)
        except IndexError:
            last_service = self.event_set.filter(event_type='Oprettelse').order_by('-start_date')[0]
            logger.info('Last service is a creation event at %s' % last_service.start_date)

        self.last_service = last_service.start_date
        self.save()

    def is_reserved(self, start_date, end_date=None):
        reservations_1 = self.reservation_set.filter(start_date__lte = start_date, end_date__gte = start_date)
    
        if end_date:
            reservations_2 = self.reservation_set.filter(start_date__lte = end_date, end_date__gte = end_date)
            reservations_3 = self.reservation_set.filter(start_date__gte = start_date, end_date__lte = end_date)
            if reservations_1.exists() or reservations_2.exists() or reservations_3.exists():
                return sorted(chain(reservations_1, reservations_2, reservations_3), key = lambda instance: instance.start_date)
            else:
                return False
        else:
            if reservations_1.exists():
                return reservations_1.order_by('start_date')
            else:
                return False

    def reserve(self, employee, construction_site, start_date, end_date):
        if self.is_reserved(start_date, end_date):
            return MESSAGES.TOOL_RESERVE_RESERVED
        if self.location == 'Kasseret':
            return MESSAGES.TOOL_RESERVE_SCRAPPED            
        elif self.location == 'Bortkommet':
            return MESSAGES.TOOL_RESERVE_LOST            
        
        reservation = Reservation(tool = self, employee = employee, 
                                  construction_site = construction_site,
                                  start_date = start_date, end_date = end_date)
        reservation.save()
        return MESSAGES.TOOL_RESERVE_SUCCESS

    def __unicode__(self):
        return self.name

class Event(models.Model):
    EVENT_TYPE_CHOICES = (
        ('Oprettelse', 'Oprettelse'),
        ('Udlån', 'Udlån'),
        ('Reparation', 'Reparation'),
        ('Kassering', 'Kassering'),
        ('Bortkommet', 'Bortkommet'),
        )
    tool = models.ForeignKey(Tool)

    employee = models.ForeignKey(Employee, verbose_name="Medarbejder", null=True, blank=True)
    construction_site = models.ForeignKey(ConstructionSite, verbose_name="Byggeplads", null=True, blank=True)

    event_type = models.CharField(choices=EVENT_TYPE_CHOICES, max_length=200)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)

    def end(self):
        if self.end_date:
            return False
        self.end_date = datetime.datetime.now()
        self.save()
        self.tool.location = "Lager"
        self.tool.employee = None
        self.tool.construction_site = None
        self.tool.save()
        return True

    def __unicode__(self):
        return "%s -> %s" % (self.tool, self.loaner)

    def get_loan_location(self):
        if self.employee and self.construction_site:
            return "%s/%s" % (self.employee, self.construction_site)
        elif self.employee:
            return self.employee
        else:
            return self.construction_site

class Login(models.Model):
    employee = models.ForeignKey(Employee)
    timestamp = models.DateTimeField(auto_now_add=True)

class Ticket(models.Model):
    LEVEL_CHOICES = (('Fejl', 'Fejl'),
                     ('Forbedring', 'Forbedring'),
                     ('Spørgsmål', 'Spørgsmål'))

    name = models.CharField('Overskrift', max_length=200)
    description = models.TextField('Beskrivelse')
    created_by = models.ForeignKey(Employee, related_name='tickets_created',
                                   verbose_name='Oprettet af',
                                   null=True, blank=True)
    reported_by = models.ForeignKey(Customer, null=True, blank=True, 
                                    default=None, 
                                    verbose_name='Rapporteret af')
    duplicate = models.ForeignKey('self', null=True, blank=True, default=None,
                                  verbose_name='Dublet af')
    is_open = models.BooleanField('Åben', default=True)
    level = models.CharField('Type', choices=LEVEL_CHOICES, max_length=200)
    assigned_to = models.ForeignKey(Employee, 
                                    related_name='tickets_assigned_to', 
                                    null=True, blank=True, default=None,
                                    verbose_name='Tildelt til')
    
    def is_closed(self):
        return not self.is_open

    def get_absolute_url(self):
        return reverse('ticket_detail', args=[self.pk])

    def __unicode__(self):
        return self.name

class TicketAnswer(models.Model):
    ticket = models.ForeignKey(Ticket)
    text = models.TextField()
    created_by = models.ForeignKey(Employee)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
class Reservation(models.Model):
    verbose_name = 'reservation'
    tool = models.ForeignKey(Tool, verbose_name='Værktøj')
    employee = models.ForeignKey(Employee, verbose_name='Medarbejder',
                                 null=True, blank=True)
    construction_site = models.ForeignKey(ConstructionSite, 
                                          verbose_name='Byggeplads',
                                          null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def reservees(self):
        if self.employee and self.construction_site:
            return "%s/%s" % (self.employee, self.construction_site)
        elif self.employee:
            return self.employee
        elif self.construction_site:
            return self.construction_site

@receiver(pre_delete, sender=Event)
def pre_delete_event(sender, instance, **kwargs):
    """
    If this event is the last recorded event for a tool, set the tool's
    location to be at store

    """
    if instance.tool.get_last_event() == instance:
        instance.tool.loaned_to = None
        instance.tool.location = 'Lager'
        instance.tool.save()


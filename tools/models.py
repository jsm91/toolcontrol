# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import datetime, re, urllib

import logging
logger = logging.getLogger(__name__)

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.mail import send_mail
from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class LoanerManager(BaseUserManager):
    def create_user(self, name, password=None):
        loaner = self.model(name=name)
        
        loaner.set_password(password)
        loaner.save(using=self._db)
        return loaner

    def create_superuser(self, name, password):
        loaner = self.create_employee(name=name, password=password)
        loaner.is_office_admin = True
        loaner.save(using=self._db)
        return loaner

class Loaner(AbstractBaseUser):
    name = models.CharField('Navn', max_length=200, unique=True, db_index=True)
    email = models.EmailField('Email', max_length=255, blank=True)
    phone_number = models.IntegerField('Telefonnummer', null=True)

    is_active = models.BooleanField('Aktiv', default=True)
    is_office_admin = models.BooleanField('Kontoradmin', default=False)
    is_tool_admin = models.BooleanField('Værktøjsadmin', default=False)
    is_loan_flagged = models.BooleanField('Låneflag', default=False)
    is_employee = models.BooleanField('Medarbejder', default=True)

    sms_loan_threshold = models.IntegerField('Min. udlån ved sms', 
                                             null=True, default=None)
    email_loan_threshold = models.IntegerField('Min. udlån ved email', 
                                               null=True, default=None)

    objects = LoanerManager()
    
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []

    def is_admin(self):
        return self.is_tool_admin or self.is_office_admin

    def send_mail(self, subject, message):
        logger.debug('Sending mail to %s with content %s' % (self.name, message))
        try:
            send_mail(subject, message, 'ToolControl <kontor@toolcontrol.dk>', 
                      [self.email])
            logger.debug('Mail successfully sent')
        except Exception, e:
            logger.debug('Mail not sent: %s' % e)

    def send_sms(self, message):
        logger.debug('Sending SMS to %s with content %s' % (self.name, message))
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

        logger.debug('SMS gateway returned "%s: %s"' % (match.group('status'),
                                                        match.group('message')))

        return match.group('status'), match.group('message')

    def get_finished_loans(self):
        return self.event_set.filter(end_date=None)

class ForgotPasswordToken(models.Model):
    token = models.CharField(max_length=200)
    user = models.ForeignKey(Loaner)

class ToolCategory(models.Model):
    name = models.CharField('Navn', max_length=200)

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
    loaned_to = models.ForeignKey(Loaner, null=True)

    invoice_number = models.IntegerField('Bilagsnummer', null=True, blank=True)
    secondary_name = models.CharField('Sekundært navn', max_length=200, 
                                      null=True, blank=True)

    def service(self):
        if self.location == 'Lager':
            event = Event(event_type='Service', tool=self)
            event.save()
            self.last_service = event.start_date
            self.save()
            return True
        else:
            return False

    def scrap(self):
        if self.location == 'Lager':
            event = Event(event_type='Kasseret', tool=self)
            event.save()
            self.location = 'Kasseret'
            self.save()
            return True
        else:
            return False

    def lost(self):
        if self.location == 'Lager':
            event = Event(event_type='Bortkommet', tool=self)
            event.save()
            self.location = 'Bortkommet'
            self.save()
            return True
        else:
            return False

    def loan(self, loaner):
        if self.location == 'Lager':
            event = Event(event_type='Udlån', tool=self, loaner=loaner)
            event.save()
            self.location = 'Udlånt'
            self.loaned_to = loaner
            self.save()
            return True
        else:
            return False

    def repair(self):
        if self.location == 'Lager':
            event = Event(event_type='Reparation', tool=self)
            event.save()
            self.location = 'Reparation'
            self.save()
            return True
        else:
            return False

    def end_loan(self):
        if self.location == 'Udlånt' or self.location == 'Reparation':
            event = self.get_last_event()
            return event.end()
        else:
            return False

    def get_last_event(self):
        return self.event_set.all().order_by('-start_date')[0]

    def update_last_service(self):
        print "Update last service"
        try:
            last_service = self.event_set.filter(event_type='Service').order_by('-start_date')[0]
        except IndexError:
            last_service = self.event_set.filter(event_type='Oprettelse').order_by('-start_date')[0]

        self.last_service = last_service.start_date
        self.save()

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
    loaner = models.ForeignKey(Loaner, null=True)
    event_type = models.CharField(choices=EVENT_TYPE_CHOICES, max_length=200)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)

    def end(self):
        if self.end_date:
            return False
        self.end_date = datetime.datetime.now()
        self.save()
        self.tool.location = "Lager"
        self.tool.loaned_to = None
        self.tool.save()
        return True

    def __unicode__(self):
        return "%s -> %s" % (self.tool, self.loaner)


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

# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Customer.subscription_price'
        db.alter_column(u'customers_customer', 'subscription_price', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'Customer.sms_price'
        db.alter_column(u'customers_customer', 'sms_price', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'Customer.credit'
        db.alter_column(u'customers_customer', 'credit', self.gf('django.db.models.fields.FloatField')())

    def backwards(self, orm):

        # Changing field 'Customer.subscription_price'
        db.alter_column(u'customers_customer', 'subscription_price', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Customer.sms_price'
        db.alter_column(u'customers_customer', 'sms_price', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Customer.credit'
        db.alter_column(u'customers_customer', 'credit', self.gf('django.db.models.fields.IntegerField')())

    models = {
        u'customers.customer': {
            'Meta': {'object_name': 'Customer'},
            'credit': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sms_price': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'sms_sent': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscription_price': ('django.db.models.fields.FloatField', [], {'default': '100'})
        }
    }

    complete_apps = ['customers']
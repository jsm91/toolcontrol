# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Customer.address'
        db.add_column(u'customers_customer', 'address',
                      self.gf('django.db.models.fields.CharField')(default='Mollerupvej 54', max_length=200),
                      keep_default=False)

        # Adding field 'Customer.zip_code'
        db.add_column(u'customers_customer', 'zip_code',
                      self.gf('django.db.models.fields.IntegerField')(default=2610),
                      keep_default=False)

        # Adding field 'Customer.town'
        db.add_column(u'customers_customer', 'town',
                      self.gf('django.db.models.fields.CharField')(default='R\xc3\xb8dovre', max_length=200),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Customer.address'
        db.delete_column(u'customers_customer', 'address')

        # Deleting field 'Customer.zip_code'
        db.delete_column(u'customers_customer', 'zip_code')

        # Deleting field 'Customer.town'
        db.delete_column(u'customers_customer', 'town')


    models = {
        u'customers.customer': {
            'Meta': {'object_name': 'Customer'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'credit': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sms_price': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'sms_sent': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscription_price': ('django.db.models.fields.FloatField', [], {'default': '100.0'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'zip_code': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['customers']
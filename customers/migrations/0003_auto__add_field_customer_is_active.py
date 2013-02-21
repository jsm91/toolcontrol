# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Customer.is_active'
        db.add_column(u'customers_customer', 'is_active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Customer.is_active'
        db.delete_column(u'customers_customer', 'is_active')


    models = {
        u'customers.customer': {
            'Meta': {'object_name': 'Customer'},
            'credit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sms_sent': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['customers']
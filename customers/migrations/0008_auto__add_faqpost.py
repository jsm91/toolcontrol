# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FAQPost'
        db.create_table(u'customers_faqpost', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.TextField')()),
            ('answer', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'customers', ['FAQPost'])


    def backwards(self, orm):
        # Deleting model 'FAQPost'
        db.delete_table(u'customers_faqpost')


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
        },
        u'customers.faqpost': {
            'Meta': {'object_name': 'FAQPost'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {})
        },
        u'customers.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'credit': ('django.db.models.fields.FloatField', [], {}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['customers.Customer']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['customers']
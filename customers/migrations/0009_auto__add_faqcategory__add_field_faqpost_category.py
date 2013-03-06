# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FAQCategory'
        db.create_table(u'customers_faqcategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'customers', ['FAQCategory'])

        # Adding field 'FAQPost.category'
        db.add_column(u'customers_faqpost', 'category',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['customers.FAQCategory']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'FAQCategory'
        db.delete_table(u'customers_faqcategory')

        # Deleting field 'FAQPost.category'
        db.delete_column(u'customers_faqpost', 'category_id')


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
        u'customers.faqcategory': {
            'Meta': {'object_name': 'FAQCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'customers.faqpost': {
            'Meta': {'object_name': 'FAQPost'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['customers.FAQCategory']"}),
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
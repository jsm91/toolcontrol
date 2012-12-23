# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Loaner'
        db.create_table(u'tools_loaner', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, db_index=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_office_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_tool_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_loan_flagged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_employee', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sms_loan_threshold', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('email_loan_threshold', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
        ))
        db.send_create_signal(u'tools', ['Loaner'])

        # Adding model 'ToolCategory'
        db.create_table(u'tools_toolcategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('total_price', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('number_of_models', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('number_of_tools', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'tools', ['ToolCategory'])

        # Adding model 'ToolModel'
        db.create_table(u'tools_toolmodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.ToolCategory'])),
            ('service_interval', self.gf('django.db.models.fields.IntegerField')(default=6)),
            ('price', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('total_price', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('number_of_tools', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'tools', ['ToolModel'])

        # Adding model 'Tool'
        db.create_table(u'tools_tool', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.ToolModel'])),
            ('service_interval', self.gf('django.db.models.fields.IntegerField')(default=6)),
            ('price', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_service', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(default=u'Lager', max_length=20)),
            ('loaned_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Loaner'], null=True)),
            ('invoice_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('secondary_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'tools', ['Tool'])

        # Adding model 'Event'
        db.create_table(u'tools_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Tool'])),
            ('loaner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Loaner'], null=True)),
            ('event_type', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'tools', ['Event'])


    def backwards(self, orm):
        # Deleting model 'Loaner'
        db.delete_table(u'tools_loaner')

        # Deleting model 'ToolCategory'
        db.delete_table(u'tools_toolcategory')

        # Deleting model 'ToolModel'
        db.delete_table(u'tools_toolmodel')

        # Deleting model 'Tool'
        db.delete_table(u'tools_tool')

        # Deleting model 'Event'
        db.delete_table(u'tools_event')


    models = {
        u'tools.event': {
            'Meta': {'object_name': 'Event'},
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loaner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Loaner']", 'null': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Tool']"})
        },
        u'tools.loaner': {
            'Meta': {'object_name': 'Loaner'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'blank': 'True'}),
            'email_loan_threshold': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_employee': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_loan_flagged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_office_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_tool_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'sms_loan_threshold': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'})
        },
        u'tools.tool': {
            'Meta': {'object_name': 'Tool'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_service': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'loaned_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Loaner']", 'null': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "u'Lager'", 'max_length': '20'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.ToolModel']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'secondary_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'service_interval': ('django.db.models.fields.IntegerField', [], {'default': '6'})
        },
        u'tools.toolcategory': {
            'Meta': {'object_name': 'ToolCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'number_of_models': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'number_of_tools': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_price': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tools.toolmodel': {
            'Meta': {'object_name': 'ToolModel'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.ToolCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'number_of_tools': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'service_interval': ('django.db.models.fields.IntegerField', [], {'default': '6'}),
            'total_price': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['tools']
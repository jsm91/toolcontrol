# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Loaner'
        db.delete_table(u'tools_loaner')

        # Adding model 'ConstructionSite'
        db.create_table(u'tools_constructionsite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'tools', ['ConstructionSite'])

        # Adding model 'Employee'
        db.create_table(u'tools_employee', (
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
            ('sms_loan_threshold', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('email_loan_threshold', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
        ))
        db.send_create_signal(u'tools', ['Employee'])


        # Changing field 'ForgotPasswordToken.user'
        db.alter_column(u'tools_forgotpasswordtoken', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Employee']))
        # Deleting field 'Event.loaner'
        db.delete_column(u'tools_event', 'loaner_id')

        # Adding field 'Event.employee'
        db.add_column(u'tools_event', 'employee',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Employee'], null=True),
                      keep_default=False)

        # Adding field 'Event.construction_site'
        db.add_column(u'tools_event', 'construction_site',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.ConstructionSite'], null=True),
                      keep_default=False)

        # Deleting field 'Tool.loaned_to'
        db.delete_column(u'tools_tool', 'loaned_to_id')

        # Adding field 'Tool.employee'
        db.add_column(u'tools_tool', 'employee',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Employee'], null=True),
                      keep_default=False)

        # Adding field 'Tool.construction_site'
        db.add_column(u'tools_tool', 'construction_site',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.ConstructionSite'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'Loaner'
        db.create_table(u'tools_loaner', (
            ('is_employee', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('phone_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sms_loan_threshold', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email_loan_threshold', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, unique=True, db_index=True)),
            ('is_tool_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_loan_flagged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_office_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'tools', ['Loaner'])

        # Deleting model 'ConstructionSite'
        db.delete_table(u'tools_constructionsite')

        # Deleting model 'Employee'
        db.delete_table(u'tools_employee')


        # Changing field 'ForgotPasswordToken.user'
        db.alter_column(u'tools_forgotpasswordtoken', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Loaner']))
        # Adding field 'Event.loaner'
        db.add_column(u'tools_event', 'loaner',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Loaner'], null=True),
                      keep_default=False)

        # Deleting field 'Event.employee'
        db.delete_column(u'tools_event', 'employee_id')

        # Deleting field 'Event.construction_site'
        db.delete_column(u'tools_event', 'construction_site_id')

        # Adding field 'Tool.loaned_to'
        db.add_column(u'tools_tool', 'loaned_to',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Loaner'], null=True),
                      keep_default=False)

        # Deleting field 'Tool.employee'
        db.delete_column(u'tools_tool', 'employee_id')

        # Deleting field 'Tool.construction_site'
        db.delete_column(u'tools_tool', 'construction_site_id')


    models = {
        u'tools.constructionsite': {
            'Meta': {'object_name': 'ConstructionSite'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'tools.employee': {
            'Meta': {'object_name': 'Employee'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'blank': 'True'}),
            'email_loan_threshold': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_loan_flagged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_office_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_tool_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'sms_loan_threshold': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'})
        },
        u'tools.event': {
            'Meta': {'object_name': 'Event'},
            'construction_site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.ConstructionSite']", 'null': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Employee']", 'null': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Tool']"})
        },
        u'tools.forgotpasswordtoken': {
            'Meta': {'object_name': 'ForgotPasswordToken'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Employee']"})
        },
        u'tools.tool': {
            'Meta': {'object_name': 'Tool'},
            'construction_site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.ConstructionSite']", 'null': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Employee']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_service': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'tools.toolmodel': {
            'Meta': {'object_name': 'ToolModel'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.ToolCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'service_interval': ('django.db.models.fields.IntegerField', [], {'default': '6'})
        }
    }

    complete_apps = ['tools']
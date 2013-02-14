# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ConstructionSite'
        db.create_table(u'tools_constructionsite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'tools', ['ConstructionSite'])

        # Adding model 'Container'
        db.create_table(u'tools_container', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['tools.ConstructionSite'], null=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'tools', ['Container'])

        # Adding model 'ContainerLoan'
        db.create_table(u'tools_containerloan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('container', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Container'])),
            ('construction_site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.ConstructionSite'])),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'tools', ['ContainerLoan'])

        # Adding model 'Employee'
        db.create_table(u'tools_employee', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, db_index=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_loan_flagged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sms_loan_threshold', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('email_loan_threshold', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
        ))
        db.send_create_signal(u'tools', ['Employee'])

        # Adding model 'ForgotPasswordToken'
        db.create_table(u'tools_forgotpasswordtoken', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Employee'])),
        ))
        db.send_create_signal(u'tools', ['ForgotPasswordToken'])

        # Adding model 'ToolCategory'
        db.create_table(u'tools_toolcategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'tools', ['ToolCategory'])

        # Adding model 'ToolModel'
        db.create_table(u'tools_toolmodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.ToolCategory'])),
            ('service_interval', self.gf('django.db.models.fields.IntegerField')(default=6)),
            ('price', self.gf('django.db.models.fields.IntegerField')(default=0)),
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
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Employee'], null=True)),
            ('construction_site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.ConstructionSite'], null=True)),
            ('container', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Container'], null=True, blank=True)),
            ('invoice_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('secondary_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('buy_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 2, 14, 0, 0))),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'tools', ['Tool'])

        # Adding model 'Event'
        db.create_table(u'tools_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Tool'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Employee'], null=True, blank=True)),
            ('construction_site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.ConstructionSite'], null=True, blank=True)),
            ('event_type', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'tools', ['Event'])

        # Adding model 'Reservation'
        db.create_table(u'tools_reservation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Tool'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.Employee'], null=True, blank=True)),
            ('construction_site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tools.ConstructionSite'], null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'tools', ['Reservation'])


    def backwards(self, orm):
        # Deleting model 'ConstructionSite'
        db.delete_table(u'tools_constructionsite')

        # Deleting model 'Container'
        db.delete_table(u'tools_container')

        # Deleting model 'ContainerLoan'
        db.delete_table(u'tools_containerloan')

        # Deleting model 'Employee'
        db.delete_table(u'tools_employee')

        # Deleting model 'ForgotPasswordToken'
        db.delete_table(u'tools_forgotpasswordtoken')

        # Deleting model 'ToolCategory'
        db.delete_table(u'tools_toolcategory')

        # Deleting model 'ToolModel'
        db.delete_table(u'tools_toolmodel')

        # Deleting model 'Tool'
        db.delete_table(u'tools_tool')

        # Deleting model 'Event'
        db.delete_table(u'tools_event')

        # Deleting model 'Reservation'
        db.delete_table(u'tools_reservation')


    models = {
        u'tools.constructionsite': {
            'Meta': {'object_name': 'ConstructionSite'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'tools.container': {
            'Meta': {'object_name': 'Container'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['tools.ConstructionSite']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'tools.containerloan': {
            'Meta': {'object_name': 'ContainerLoan'},
            'construction_site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.ConstructionSite']"}),
            'container': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Container']"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'tools.employee': {
            'Meta': {'object_name': 'Employee'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'blank': 'True'}),
            'email_loan_threshold': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_loan_flagged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sms_loan_threshold': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'})
        },
        u'tools.event': {
            'Meta': {'object_name': 'Event'},
            'construction_site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.ConstructionSite']", 'null': 'True', 'blank': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Employee']", 'null': 'True', 'blank': 'True'}),
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
        u'tools.reservation': {
            'Meta': {'object_name': 'Reservation'},
            'construction_site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.ConstructionSite']", 'null': 'True', 'blank': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Employee']", 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Tool']"})
        },
        u'tools.tool': {
            'Meta': {'object_name': 'Tool'},
            'buy_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 2, 14, 0, 0)'}),
            'construction_site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.ConstructionSite']", 'null': 'True'}),
            'container': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Container']", 'null': 'True', 'blank': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Employee']", 'null': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
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
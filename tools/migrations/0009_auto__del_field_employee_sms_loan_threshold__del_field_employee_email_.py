# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Employee.sms_loan_threshold'
        db.delete_column(u'tools_employee', 'sms_loan_threshold')

        # Deleting field 'Employee.email_loan_threshold'
        db.delete_column(u'tools_employee', 'email_loan_threshold')

        # Adding field 'Employee.loan_threshold'
        db.add_column(u'tools_employee', 'loan_threshold',
                      self.gf('django.db.models.fields.IntegerField')(default=None, null=True),
                      keep_default=False)

        # Adding field 'Employee.receive_sms'
        db.add_column(u'tools_employee', 'receive_sms',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Employee.receive_mail'
        db.add_column(u'tools_employee', 'receive_mail',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Employee.sms_loan_threshold'
        db.add_column(u'tools_employee', 'sms_loan_threshold',
                      self.gf('django.db.models.fields.IntegerField')(default=None, null=True),
                      keep_default=False)

        # Adding field 'Employee.email_loan_threshold'
        db.add_column(u'tools_employee', 'email_loan_threshold',
                      self.gf('django.db.models.fields.IntegerField')(default=None, null=True),
                      keep_default=False)

        # Deleting field 'Employee.loan_threshold'
        db.delete_column(u'tools_employee', 'loan_threshold')

        # Deleting field 'Employee.receive_sms'
        db.delete_column(u'tools_employee', 'receive_sms')

        # Deleting field 'Employee.receive_mail'
        db.delete_column(u'tools_employee', 'receive_mail')


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
        u'tools.constructionsite': {
            'Meta': {'object_name': 'ConstructionSite'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['customers.Customer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'tools.container': {
            'Meta': {'object_name': 'Container'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['customers.Customer']"}),
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
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['customers.Customer']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_loan_flagged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'loan_threshold': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'receive_mail': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_sms': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
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
        u'tools.login': {
            'Meta': {'object_name': 'Login'},
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Employee']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
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
        u'tools.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'tickets_assigned_to'", 'null': 'True', 'blank': 'True', 'to': u"orm['tools.Employee']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'tickets_created'", 'null': 'True', 'to': u"orm['tools.Employee']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'duplicate': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['tools.Ticket']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'reported_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['customers.Customer']", 'null': 'True', 'blank': 'True'})
        },
        u'tools.ticketanswer': {
            'Meta': {'object_name': 'TicketAnswer'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Employee']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tools.Ticket']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'tools.tool': {
            'Meta': {'object_name': 'Tool'},
            'buy_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 6, 0, 0)'}),
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
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['customers.Customer']"}),
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
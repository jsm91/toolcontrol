# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Container.customer'
        db.add_column(u'tools_container', 'customer',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['admin.Customer']),
                      keep_default=False)

        # Adding field 'ToolCategory.customer'
        db.add_column(u'tools_toolcategory', 'customer',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['admin.Customer']),
                      keep_default=False)

        # Adding field 'ConstructionSite.customer'
        db.add_column(u'tools_constructionsite', 'customer',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['admin.Customer']),
                      keep_default=False)

        # Adding field 'Employee.customer'
        db.add_column(u'tools_employee', 'customer',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admin.Customer'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Container.customer'
        db.delete_column(u'tools_container', 'customer_id')

        # Deleting field 'ToolCategory.customer'
        db.delete_column(u'tools_toolcategory', 'customer_id')

        # Deleting field 'ConstructionSite.customer'
        db.delete_column(u'tools_constructionsite', 'customer_id')

        # Deleting field 'Employee.customer'
        db.delete_column(u'tools_employee', 'customer_id')


    models = {
        u'admin.customer': {
            'Meta': {'object_name': 'Customer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sms_sent': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tools.constructionsite': {
            'Meta': {'object_name': 'ConstructionSite'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.Customer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'tools.container': {
            'Meta': {'object_name': 'Container'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.Customer']"}),
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
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.Customer']", 'null': 'True', 'blank': 'True'}),
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
            'buy_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 2, 19, 0, 0)'}),
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
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.Customer']"}),
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
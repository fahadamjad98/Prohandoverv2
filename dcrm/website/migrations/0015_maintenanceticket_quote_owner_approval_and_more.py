# Generated by Django 5.0 on 2024-04-24 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0014_record_tenant_doc_info_1_record_tenant_doc_info_2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenanceticket',
            name='quote_owner_approval',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='maintenanceticket',
            name='quote_tenant_approval',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='maintenanceticket',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='maintenanceticket',
            name='owner_approval',
            field=models.CharField(choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Fixed', 'Fixed'), ('Pending Approval', 'Pending Approval'), ('Approved for Inspection', 'Approved for Inspection'), ('Rejected for Inspection', 'Rejected for Inspection'), ('Inspection Done', 'Inspection Done'), ('Quotation Created', 'Quotation Created'), ('Quotation Approved By Owner', 'Quotation Approved By Owner'), ('Quotation Approved By Tenant', 'Quotation Approved By Tenant'), ('Quotation Rejected By Owner', 'Quotation Rejected By Owner'), ('Quotation Rejected By Tenant', 'Quotation Rejected By Tenant'), ('Issue Resolved', 'Issue Resolved'), ('Issue Not Resolved', 'Issue Not Resolved')], default='Pending Approval', max_length=60),
        ),
    ]

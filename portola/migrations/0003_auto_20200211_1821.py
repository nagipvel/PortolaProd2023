# Generated by Django 2.2.7 on 2020-02-11 18:21

from django.db import migrations, models
import django.utils.timezone
import portola.models


class Migration(migrations.Migration):

    dependencies = [
        ('portola', '0002_init_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='disclosure',
            field=models.CharField(choices=[['GENERAL', 'General'], ['BY REQUEST', 'By Request'], ['UNAVAILABLE', 'Undisclosed'], ['PENDING', 'Pending Authorization'], ['VDP', 'VDP']], db_index=True, default='GENERAL', max_length=100),
        ),
        migrations.AlterField(
            model_name='document',
            name='issued_date',
            field=models.DateField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='document',
            name='product_type',
            field=models.CharField(choices=[['modules', 'modules'], ['racking', 'racking'], ['inverter', 'inverter'], ['optimizer', 'optimizer']], db_index=True, default='MODULES', max_length=32),
        ),
        migrations.AlterField(
            model_name='document',
            name='title',
            field=models.CharField(blank=True, db_index=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='document',
            name='type',
            field=models.CharField(choices=[['REPORT', 'Report'], ['RAW', 'Raw'], ['PAN', 'PAN File'], ['MIAM', 'Module IAM Report'], ['PANRPT', 'PAN Report'], ['FER', 'field exposure rpt'], ['FINREL', 'final reliability'], ['interim1 reliability', 'interim1 reliability'], ['interim2', 'interim2'], ['LID', 'LID'], ['INTAKE', 'Intake'], ['FWR', 'Factory Witness Report'], ['financials(VDP)', 'financials(VDP)'], ['IFT', 'Inverter Field Testing - Other'], ['IPQPF', 'Inverter PQP Final'], ['IPQPILT', 'Inverter PQP Interim Lab Test'], ['MFT', 'Module Field Testing - Other'], ['MINTAKE', 'Module Intake'], ['MLID', 'Module LID'], ['MDML', 'Module Mechanical Load (Static, Dynamic, Other)'], ['MNOCT', 'Module NOCT'], ['MPANF', 'Module PAN File'], ['MPANR', 'Module PAN Report'], ['MPID', 'Module PID Testing'], ['MPQPF', 'Module PQP Final'], ['MPQPFE', 'Module PQP Field Exposure'], ['MPQPI1', 'Module PQP Interim 1'], ['MPQPI2', 'Module PQP Interim 2'], ['MPQPI3', 'Module PQP Interim 3'], ['MISC', 'Miscellaneous'], ['MCEY', 'Module Comparative Energy Yield'], ['RIE', 'Racking Installation Efficiency']], db_index=True, default='REPORT', max_length=32),
        ),
        migrations.AlterField(
            model_name='entity',
            name='legal_name',
            field=models.CharField(db_index=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='entity',
            name='type',
            field=models.CharField(choices=[['PARTNER', 'Downstream Partner'], ['CLIENT', 'Downstream Client'], ['MANUFACTURER', 'Manufacturer'], ['PVEL', 'PVEL']], db_index=True, default='DOWNSTREAM', max_length=100),
        ),
        migrations.AlterField(
            model_name='follow',
            name='create_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='number',
            field=models.CharField(blank=True, db_index=True, max_length=16),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[['ACTIVE', 'ACTIVE'], ['INACTIVE', 'INACTIVE']], db_index=True, default='ACTIVE', max_length=100),
        ),
        migrations.AlterField(
            model_name='project',
            name='type',
            field=models.CharField(choices=[['MPQP', 'Module PQP'], ['IPQP', 'Inverter PQP'], ['SPQP', 'Storage PQP']], db_index=True, default='MPQP', max_length=100),
        ),
        migrations.AlterField(
            model_name='request',
            name='expires',
            field=models.DateField(blank=True, db_index=True, default=portola.models._request_expiration, null=True),
        ),
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[['ACTIVE', 'ACTIVE'], ['APPROVED', 'APPROVED'], ['REFUSED', 'REFUSED'], ['EXPIRED', 'EXPIRED']], db_index=True, default='ACTIVE', max_length=100),
        ),
        migrations.AlterField(
            model_name='technologytag',
            name='title',
            field=models.CharField(db_index=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='technologytag',
            name='type',
            field=models.CharField(choices=[['Tracker Type', 'Tracker Type'], ['Racking Type', 'Racking Type'], ['Power Bin', 'Power Bin'], ['Mounting Type', 'Mounting Type'], ['Misc', 'Misc'], ['Max Voltage', 'Max Voltage'], ['Inverter Type', 'Inverter Type'], ['Cell Type', 'Cell Type'], ['Cell Count', 'Cell Count'], ['Cell Chemistry', 'Cell Chemistry'], ['Battery Type', 'Battery Type'], ['Battery Testing', 'Battery Testing']], db_index=True, default='Power Bin', max_length=32),
        ),
    ]

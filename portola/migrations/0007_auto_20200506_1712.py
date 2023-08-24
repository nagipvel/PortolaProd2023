# Generated by Django 2.2.7 on 2020-05-06 17:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import portola.models


class Migration(migrations.Migration):

    dependencies = [
        ('portola', '0006_auto_20200502_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='disclosure',
            field=models.CharField(choices=[['GENERAL', 'General'], ['BY REQUEST', 'By Request'], ['UNAVAILABLE', 'Undisclosed'], ['PENDING', 'Pending Authorization'], ['VDP', 'VDP']], db_index=True, default='PENDING', max_length=100),
        ),
        migrations.AlterField(
            model_name='document',
            name='entity',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='document_entity', to='portola.Entity'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='document',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='document',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='document_project', to='portola.Project'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='document',
            name='title',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='entity',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='portola.Company'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profile',
            name='entity',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='portola.Entity'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='project',
            name='number',
            field=models.CharField(db_index=True, max_length=16),
        ),
        migrations.AlterField(
            model_name='request',
            name='expires',
            field=models.DateField(db_index=True, default=portola.models._request_expiration),
        ),
    ]

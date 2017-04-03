# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-03-31 11:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0009_4_14_updates'),
    ]

    operations = [
        migrations.RenameField(
            model_name='error',
            old_name='date',
            new_name='created_at',
        ),
        migrations.AlterField(
            model_name='error',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name='date',
            ),
            preserve_default=False,
        ),
        migrations.RenameField(
            model_name='error',
            old_name='error',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='error',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.RenameField(
            model_name='fault',
            old_name='faultdef',
            new_name='fault_definition',
        ),
        migrations.RenameField(
            model_name='fault',
            old_name='text',
            new_name='result',
        ),
        migrations.AlterField(
            model_name='fault',
            name='result',
            field=models.TextField(blank=True, null=True, verbose_name='result'),
        ),
        migrations.RenameField(
            model_name='fault',
            old_name='date',
            new_name='created_at',
        ),
        migrations.AlterField(
            model_name='fault',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name='date',
            ),
            preserve_default=False,
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_checking SET code=%s WHERE id=2;",
                [
                    "from migasfree.server.models import Fault\nfrom django.db.models import Q\nresult = Fault.objects.filter(checked__exact=0).filter(Q(fault_definition__users__id__in=[request.user.id,]) | Q(fault_definition__users=None)).count()\nurl = '/admin/server/fault/?checked__exact=0&user=me'\nalert = 'danger'\nmsg = 'Faults to check'\ntarget = 'computer'\n"
                ]
            )],
            [(
                "UPDATE server_checking SET code=%s WHERE id=2;",
                [
                    "from migasfree.server.models import Fault\nfrom django.db.models import Q\nresult = Fault.objects.filter(checked__exact=0).filter(Q(faultdef__users__id__in=[request.user.id,]) | Q(faultdef__users=None)).count()\nurl = '/admin/server/fault/?checked__exact=0&user=me'\nalert = 'danger'\nmsg = 'Faults to check'\ntarget = 'computer'\n"
                ]
            )]
        ),
        migrations.RenameField(
            model_name='migration',
            old_name='date',
            new_name='created_at',
        ),
        migrations.AlterField(
            model_name='migration',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name='date',
            ),
            preserve_default=False,
        ),
    ]

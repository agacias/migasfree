# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Query(models.Model):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    description = models.TextField(
        verbose_name=_("description"),
        null=True,
        blank=True
    )

    code = models.TextField(
        verbose_name=_("code"),
        null=True,
        blank=True,
        help_text=_("%s: project = user.project, query = QuerySet, fields = list of QuerySet fields names to show, titles = list of QuerySet fields titles") % _("Django Code"),
        default="query = Package.objects.filter(project=PROJECT).filter(deployment__id__exact=None)\nfields = ('id', 'name', 'store__name')\ntitles = ('id', 'name', 'store')"
    )

    parameters = models.TextField(
        verbose_name=_("parameters"),
        null=True,
        blank=True,
        help_text=_("Django Code")
    )

    @staticmethod
    def get_query_names():
        return Query.objects.values_list('id', 'name').order_by('name')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Query")
        verbose_name_plural = _("Queries")
        permissions = (("can_save_query", "Can save Query"),)

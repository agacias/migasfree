# -*- coding: utf-8 -*-

import re

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import Project, AutoCheckError
from .event import Event


class DomainErrorManager(models.Manager):
    def scope(self, user):
        qs = super(DomainErrorManager, self).get_queryset()
        if not user.is_view_all():
            qs = qs.filter(
                project_id__in=user.get_projects(),
                computer_id__in=user.get_computers()
            )

        return qs


class UncheckedManager(DomainErrorManager):
    def get_queryset(self):
        return super(UncheckedManager, self).get_queryset().filter(
            checked=0
        )

    def scope(self, user):
        return super(UncheckedManager, self).scope(user).filter(
            checked=0
        )


class ErrorManager(DomainErrorManager):
    def create(self, computer, project, description):
        obj = Error()
        obj.computer = computer
        obj.project = project
        obj.description = description
        obj.save()

        return obj


class Error(Event):
    description = models.TextField(
        verbose_name=_("description"),
        null=True,
        blank=True
    )

    checked = models.BooleanField(
        verbose_name=_("checked"),
        default=False,
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("project")
    )

    objects = ErrorManager()
    unchecked = UncheckedManager()

    @staticmethod
    def unchecked_count(user):
        return Error.unchecked.scope(user).count()

    def checked_ok(self):
        self.checked = True
        self.save()

    def auto_check(self):
        for ace in AutoCheckError.objects.all():
            if re.search(ace.message, self.description):
                self.checked = True
                return

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.description = self.description.replace("\r\n", "\n")
        self.auto_check()
        super(Error, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        app_label = 'server'
        verbose_name = _("Error")
        verbose_name_plural = _("Errors")
        permissions = (("can_save_error", "Can save Error"),)

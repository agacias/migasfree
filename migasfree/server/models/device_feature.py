# -*- coding: utf-8 *-*

from django.db import models
from django.utils.translation import ugettext_lazy as _
from . import MigasLink


class DeviceFeature(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Feature")
        verbose_name_plural = _("Features")
        permissions = (("can_save_devicefeature", "Can save Device Feature"),)

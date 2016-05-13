# -*- coding: utf-8 -*-

import django_filters

from django.contrib.admin.filters import ChoicesFieldListFilter
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.utils.translation import ugettext as _
from rest_framework import filters

from .models import (
    ClientProperty, TagType, Computer,
    Store, Property, Version, Attribute,
    Package, Repository, Error, FaultDef,
    Fault, Notification, Migration,
    HwNode, Checking,
)


class ProductiveFilterSpec(ChoicesFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super(ProductiveFilterSpec, self).__init__(field, request, params,
            model, model_admin, field_path)
        self.lookup_kwarg = '%s__in' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        self.title = _('Status')

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
            'display': _('All')
        }

        yield {
            'selected': self.lookup_val == 'intended,reserved,unknown,available,in repair',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'intended,reserved,unknown,available,in repair'}
            ),
            'display': _("Subscribed")
        }

        yield {
            'selected': self.lookup_val == 'intended,reserved,unknown',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'intended,reserved,unknown'}
            ),
            'display': "* " + _("Productive")
        }

        yield {
            'selected': self.lookup_val == 'intended',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'intended'}
            ),
            'display': "--- " + _("intended")
        }

        yield {
            'selected': self.lookup_val == 'reserved',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'reserved'}
            ),
            'display': "--- " + _("reserved")
        }

        yield {
            'selected': self.lookup_val == 'unknown',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'unknown'}
            ),
            'display': "--- " + _("unknown")
        }

        yield {
            'selected': self.lookup_val == 'available,in repair',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'available,in repair'}
            ),
            'display': "* " + _("Unproductive")
        }

        yield {
            'selected': self.lookup_val == 'in repair',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'in repair'}
            ),
            'display': "--- " + _("in repair")
        }

        yield {
            'selected': self.lookup_val == 'available',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'available'}
            ),
            'display': "--- " + _("available")
        }

        yield {
            'selected': self.lookup_val == 'unsubscribed',
            'query_string': cl.get_query_string(
                {self.lookup_kwarg: 'unsubscribed'}
            ),
            'display': _("unsubscribed")
        }


class TagFilter(SimpleListFilter):
    title = _('Tag Type')
    parameter_name = 'Tag'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in TagType.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(property_att__id__exact=self.value())
        else:
            return queryset


class FeatureFilter(SimpleListFilter):
    title = _('Property')
    parameter_name = 'Attribute'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in ClientProperty.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(property_att__id__exact=self.value())
        else:
            return queryset


class UserFaultFilter(SimpleListFilter):
    title = _('User')
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        return (
            ('me', _('To check for me')),
            ('only_me', _('Assigned to me')),
            ('others', _('Assigned to others')),
            ('no_assign', _('Not assigned')),
        )

    def queryset(self, request, queryset):
        lst = [request.user.id]
        if self.value() == 'me':
            return queryset.filter(
                Q(faultdef__users__id__in=lst) | Q(faultdef__users=None)
            )
        elif self.value() == 'only_me':
            return queryset.filter(Q(faultdef__users__id__in=lst))
        elif self.value() == 'others':
            return queryset.exclude(
                faultdef__users__id__in=lst
            ).exclude(faultdef__users=None)
        elif self.value() == 'no_assign':
            return queryset.filter(Q(faultdef__users=None))


class AttributeFilter(filters.FilterSet):
    class Meta:
        model = Attribute
        fields = ['property_att']


class CheckingFilter(filters.FilterSet):
    class Meta:
        model = Checking
        fields = ['active', 'alert']


class ComputerFilter(filters.FilterSet):
    platform = django_filters.CharFilter(name='version__platform__id')
    created_at = django_filters.DateFilter(name='dateinput', lookup_type='gte')
    mac_address = django_filters.CharFilter(
        name='mac_address', lookup_type='icontains'
    )

    class Meta:
        model = Computer
        fields = ['version__id', 'status', 'name']


class ErrorFilter(filters.FilterSet):
    date = django_filters.DateFilter(name='date', lookup_type='gte')

    class Meta:
        model = Error
        fields = ['version__id', 'checked', 'computer__id']


class FaultDefinitionFilter(filters.FilterSet):
    class Meta:
        model = FaultDef
        fields = ['attributes__id', 'active']


class FaultFilter(filters.FilterSet):
    created_at = django_filters.DateFilter(name='created_at', lookup_type='gte')

    class Meta:
        model = Fault
        fields = [
            'version__id', 'checked', 'faultdef__id', 'computer__id'
        ]


class MigrationFilter(filters.FilterSet):
    created_at = django_filters.DateFilter(name='created_at', lookup_type='gte')

    class Meta:
        model = Migration
        fields = ['version__id', 'computer__id']


class NodeFilter(filters.FilterSet):
    class Meta:
        model = HwNode
        fields = [
            'computer__id', 'id', 'parent', 'product', 'level',
            'width', 'name', 'classname', 'enabled', 'claimed',
            'description', 'vendor', 'serial', 'businfo', 'physid',
            'slot', 'size', 'capacity', 'clock', 'dev'
        ]


class NotificationFilter(filters.FilterSet):
    created_at = django_filters.DateFilter(name='created_at', lookup_type='gte')

    class Meta:
        model = Notification
        fields = ['checked']


class PackageFilter(filters.FilterSet):
    class Meta:
        model = Package
        fields = ['version__id', 'store__id']


class PropertyFilter(filters.FilterSet):
    class Meta:
        model = Property
        fields = ['active', 'tag']


class RepositoryFilter(filters.FilterSet):
    included_attributes = django_filters.CharFilter(
        name='attributes__value', lookup_type='icontains'
    )
    excluded_attributes = django_filters.CharFilter(
        name='excludes__value', lookup_type='icontains'
    )
    available_packages = django_filters.CharFilter(
        name='packages__name', lookup_type='icontains'
    )

    class Meta:
        model = Repository
        fields = ['version__id', 'active', 'schedule__id']


class StoreFilter(filters.FilterSet):
    class Meta:
        model = Store
        fields = ['version__id']


class VersionFilter(filters.FilterSet):
    class Meta:
        model = Version
        fields = ['platform__id']

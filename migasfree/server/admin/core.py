# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.html import format_html
from django.db.models import Prefetch

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

from .migasfree import MigasAdmin, MigasFields

from ..models import (
    Attribute, AttributeSet, ClientProperty, ClientAttribute, Computer,
    Notification, Package, Platform, Pms, Property, Query, Deployment, Schedule,
    ScheduleDelay, Store, ServerAttribute, ServerProperty, UserProfile, Project,
    Domain, Scope,
)

from ..forms import (
    PropertyForm, DeploymentForm, ServerAttributeForm,
    AttributeSetForm, StoreForm, PackageForm, UserProfileForm,
    DomainForm, ScopeForm
)

from ..filters import (
    ClientAttributeFilter, ServerAttributeFilter,
    ProjectFilterAdmin, PlatformFilterAdmin,
    DomainFilter
)

from ..resources import AttributeResource

from ..utils import compare_list_values
from ..tasks import (
    create_repository_metadata,
    remove_repository_metadata
)


@admin.register(AttributeSet)
class AttributeSetAdmin(MigasAdmin):
    form = AttributeSetForm
    list_display = ('name_link', 'my_enabled')
    list_filter = ('enabled',)
    ordering = ('name',)
    search_fields = ('name', 'included_attributes__value', 'excluded_attributes__value')

    name_link = MigasFields.link(model=AttributeSet, name='name')
    my_enabled = MigasFields.boolean(model=AttributeSet, name='enabled')

    def get_queryset(self, request):
        qs = Attribute.objects.scope(request.user.userprofile)
        return super(AttributeSetAdmin, self).get_queryset(
            request
        ).prefetch_related(
            Prefetch('included_attributes', queryset=qs),
            'included_attributes__property_att',
            Prefetch('excluded_attributes', queryset=qs),
            'excluded_attributes__property_att'
        )


@admin.register(Attribute)
class AttributeAdmin(MigasAdmin):
    list_display = (
        'value_link', 'description', 'total_computers', 'property_link'
    )
    list_select_related = ('property_att',)
    list_filter = (ClientAttributeFilter,)
    fields = ('property_link', 'value', 'description')
    ordering = ('property_att', 'value')
    search_fields = ('value', 'description')
    readonly_fields = ('property_link', 'value')

    value_link = MigasFields.link(model=Attribute, name='value')
    property_link = MigasFields.link(
        model=Attribute,
        name='property_att',
        order='property_att__name'
    )

    resource_class = AttributeResource

    def get_queryset(self, request):
        sql = Attribute.TOTAL_COMPUTER_QUERY
        user = request.user.userprofile
        if not user.is_view_all():
            computers = user.get_computers()
            if computers:
                sql += " AND server_computer_sync_attributes.computer_id in " \
                    + "(" + ",".join(str(x) for x in computers) + ")"
        return Attribute.objects.scope(user).extra(
            select={'total_computers': sql}
        )

    def has_add_permission(self, request):
        return False


@admin.register(ClientAttribute)
class ClientAttributeAdmin(MigasAdmin):
    list_display = (
        'value_link', 'description', 'total_computers', 'property_link'
    )
    list_select_related = ('property_att',)
    list_filter = (ClientAttributeFilter,)
    fields = ('property_link', 'value', 'description')
    ordering = ('property_att', 'value')
    search_fields = ('value', 'description')
    readonly_fields = ('property_link', 'value')

    value_link = MigasFields.link(model=ClientAttribute, name='value')
    property_link = MigasFields.link(
        model=ClientAttribute,
        name='property_att',
        order='property_att__name',
        description=_('Formula')
    )

    resource_class = AttributeResource

    def get_queryset(self, request):
        sql = Attribute.TOTAL_COMPUTER_QUERY
        user = request.user.userprofile
        if not user.is_view_all():
            computers = user.get_computers()
            if computers:
                sql += " AND server_computer_sync_attributes.computer_id in " \
                    + "(" + ",".join(str(x) for x in computers) + ")"
        return ClientAttribute.objects.scope(user).extra(
            select={'total_computers': sql}
        )

    def has_add_permission(self, request):
        return False


@admin.register(Package)
class PackageAdmin(MigasAdmin):
    form = PackageForm
    readonly_fields = ('deployments_link',)
    fieldsets = (
        ('', {
            'fields': (
                'name',
                'project',
                'store',
                'deployments_link',
            )
        }),
    )
    list_display = (
        'name_link', 'project_link', 'store_link', 'deployments_link'
    )
    list_filter = (('project', ProjectFilterAdmin), 'store', 'deployment')
    list_select_related = ('project', 'store')
    search_fields = ('name', 'store__name')
    ordering = ('name',)

    name_link = MigasFields.link(model=Package, name='name')
    project_link = MigasFields.link(
        model=Package, name='project', order='project__name'
    )
    store_link = MigasFields.link(
        model=Package, name='store', order='store__name'
    )
    deployments_link = MigasFields.objects_link(
        model=Package, name='deployment_set'
    )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == '++':
            # Packages filter by user project
            kwargs['queryset'] = Store.objects.filter(
                project__id=request.user.userprofile.project_id
            )

            return db_field.formfield(**kwargs)

        return super(PackageAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    class Media:
        js = ('js/package_admin.js',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(PackageAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        return super(PackageAdmin, self).get_queryset(
            request
        ).prefetch_related(
            Prefetch('deployment_set', queryset=Deployment.objects.scope(request.user.userprofile))
        )


@admin.register(Platform)
class PlatformAdmin(MigasAdmin):
    list_display = ('name_link',)
    actions = ['delete_selected']
    search_fields = ('name',)

    name_link = MigasFields.link(model=Platform, name='name')

    def delete_selected(self, request, objects):
        if not self.has_delete_permission(request):
            raise PermissionDenied

        return render(
            request,
            'platform_confirm_delete_selected.html',
            {
                'object_list': ', '.join([x.__str__() for x in objects])
            }
        )

    delete_selected.short_description = _("Delete selected "
                                          "%(verbose_name_plural)s")


@admin.register(Pms)
class PmsAdmin(MigasAdmin):
    list_display = ('name_link',)
    search_fields = ('name',)

    name_link = MigasFields.link(model=Pms, name='name')


@admin.register(ClientProperty)
class ClientPropertyAdmin(MigasAdmin):
    list_display = ('name_link', 'my_enabled', 'kind', 'my_auto_add')
    list_filter = ('enabled', 'kind', 'auto_add')
    ordering = ('name',)
    search_fields = ('name', 'prefix')
    form = PropertyForm
    actions = None

    fieldsets = (
        (_('General'), {
            'fields': (
                'prefix',
                'name',
                'kind',
                'enabled',
                'auto_add',
            )
        }),
        (_('Code'), {
            'fields': (
                'language',
                'code',
            )
        }),
    )

    name_link = MigasFields.link(model=ClientProperty, name='name')
    my_enabled = MigasFields.boolean(model=ClientProperty, name='enabled')
    my_auto_add = MigasFields.boolean(model=ClientProperty, name='auto_add')


@admin.register(Property)
class PropertyAdmin(ClientPropertyAdmin):
    list_display = ('name_link', 'my_enabled', 'kind', 'my_auto_add', 'sort')
    search_fields = ('name',)

    fieldsets = (
        (_('General'), {
            'fields': (
                'sort',
                'prefix',
                'name',
                'kind',
                'enabled',
                'auto_add',
            )
        }),
        (_('Code'), {
            'fields': (
                'language',
                'code',
            )
        }),
    )


@admin.register(ServerProperty)
class ServerPropertyAdmin(MigasAdmin):
    list_display = ('name_link', 'prefix', 'kind', 'my_enabled')
    fields = ('prefix', 'name', 'kind', 'enabled')
    search_fields = ('name', 'prefix')
    list_filter = ('enabled', 'kind')

    name_link = MigasFields.link(model=ServerProperty, name='name')
    my_enabled = MigasFields.boolean(model=ServerProperty, name='enabled')


@admin.register(Query)
class QueryAdmin(MigasAdmin):
    list_display = ('name', 'description')
    list_display_links = ('name',)
    actions = ['run_query']
    search_fields = ('name', 'description')
    ordering = ('name',)

    def run_query(self, request, queryset):
        for query in queryset:
            return redirect(reverse('query', args=(query.id,)))

    run_query.short_description = _("Run Query")


@admin.register(Deployment)
class DeploymentAdmin(AjaxSelectAdmin, MigasAdmin):
    form = DeploymentForm
    list_display = (
        'name_link', 'project_link', 'domain_link',
        'my_enabled', 'start_date', 'schedule_link', 'timeline', 'computers',
    )
    list_filter = ('enabled', ('project', ProjectFilterAdmin), DomainFilter)
    search_fields = ('name', 'available_packages__name')
    list_select_related = ("project",)
    actions = ['regenerate_metadata']
    readonly_fields = ('timeline',)

    fieldsets = (
        (_('General'), {
            'fields': ('name', 'project', 'enabled', 'comment',)
        }),
        (_('Packages'), {
            'classes': ('collapse',),
            'fields': (
                'available_packages',
                'packages_to_install',
                'packages_to_remove',
            )
        }),
        (_('Default'), {
            'classes': ('collapse',),
            'fields': (
                'default_preincluded_packages',
                'default_included_packages',
                'default_excluded_packages',
            )
        }),
        (_('Attributes'), {
            'fields': ('domain', 'included_attributes', 'excluded_attributes')
        }),
        (_('Schedule'), {
            'fields': ('start_date', 'schedule', 'timeline')
        }),
    )

    name_link = MigasFields.link(model=Deployment, name='name')
    project_link = MigasFields.link(
        model=Deployment, name='project', order='project__name'
    )
    domain_link = MigasFields.link(
        model=Deployment, name='domain', order='domain__name'
    )
    schedule_link = MigasFields.link(
        model=Deployment, name='schedule', order='schedule__name'
    )
    my_enabled = MigasFields.boolean(model=Deployment, name='enabled')
    timeline = MigasFields.timeline()

    def computers(self, obj):
        related_objects = obj.related_objects('computer',self.user.userprofile)
        if related_objects:
            return related_objects.count()
        return 0
    computers.short_description = _('Computers')

    def regenerate_metadata(self, request, objects):
        if not self.has_change_permission(request):
            raise PermissionDenied

        for deploy in objects:
            create_repository_metadata(deploy, request=request)

    regenerate_metadata.short_description = _("Regenerate metadata")

    def save_model(self, request, obj, form, change):
        is_new = (obj.pk is None)
        has_name_changed = form.initial.get('name') != obj.name
        packages_after = map(int, form.cleaned_data.get('available_packages'))

        user = request.user.userprofile

        if user.domain_preference and user.domain_preference == obj.domain:
            if not obj.name.startswith(user.domain_preference.name.lower()):
                obj.name = u'{}_{}'.format(user.domain_preference.name.lower(), obj.name)

        super(DeploymentAdmin, self).save_model(request, obj, form, change)

        # create physical repository when packages have been changed
        # or repository does not have packages at first time
        # or name has been changed (to avoid client errors)
        if ((is_new and len(packages_after) == 0)
                or compare_list_values(
                    obj.available_packages.values_list('id', flat=True),  # packages before
                    packages_after
                ) is False) or has_name_changed:
            create_repository_metadata(obj, packages_after, request)

            # delete old repository by name change
            if has_name_changed and not is_new:
                remove_repository_metadata(request, obj, form.initial.get('name'))

        Notification.objects.create(
            ugettext('Deployment [%s] modified by user [%s] (<a href="%s">review changes</a>)') % (
                '<a href="{}">{}</a>'.format(
                    reverse('admin:server_deployment_change', args=(obj.id,)),
                    obj.name
                ),
                request.user,
                reverse('admin:server_deployment_history', args=(obj.id,))
            )
        )

    def get_queryset(self, request):
        self.user = request.user
        qs = Attribute.objects.scope(request.user.userprofile)
        return super(DeploymentAdmin, self).get_queryset(
            request
        ).prefetch_related(
            Prefetch('included_attributes', queryset=qs),
            'included_attributes__property_att',
            Prefetch('excluded_attributes', queryset=qs),
            'excluded_attributes__property_att',
        ).extra(
            select={
                'schedule_begin': '(SELECT delay FROM server_scheduledelay '
                                  'WHERE server_deployment.schedule_id = server_scheduledelay.schedule_id '
                                  'ORDER BY server_scheduledelay.delay LIMIT 1)',
                'schedule_end': '(SELECT delay+duration FROM server_scheduledelay '
                                'WHERE server_deployment.schedule_id = server_scheduledelay.schedule_id '
                                'ORDER BY server_scheduledelay.delay DESC LIMIT 1)'
            }
        ).select_related("project", "schedule")

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(
            '{}?enabled__exact={}&project__id__exact={}'.format(
                reverse('admin:server_deployment_changelist'),
                obj.enabled,
                obj.project.id
            )
        )

    def response_change(self, request, obj):
        if request.POST.get('_save', None):
            return HttpResponseRedirect(
                '{}?enabled__exact={}&project__id__exact={}'.format(
                    reverse('admin:server_deployment_changelist'),
                    obj.enabled,
                    obj.project.id
                )
            )

        return super(DeploymentAdmin, self).response_change(request, obj)


class ScheduleDelayLine(admin.TabularInline):
    model = ScheduleDelay
    fields = ('delay', 'attributes', 'computers', 'duration')
    form = make_ajax_form(ScheduleDelay, {'attributes': 'attribute'})
    ordering = ('delay',)
    readonly_fields = ('computers',)
    extra = 0

    def computers(self, obj):
        related_objects = obj.related_objects('computer',self.request.user.userprofile)
        if related_objects:
            return related_objects.count()
        return 0
    computers.short_description = _('Computers')

    def get_queryset(self, request):
        self.request = request
        qs = Attribute.objects.scope(request.user.userprofile)

        return super(ScheduleDelayLine, self).get_queryset(
            request
        ).prefetch_related(
            Prefetch('attributes', queryset=qs),
            'attributes__property_att',
        )


@admin.register(Schedule)
class ScheduleAdmin(MigasAdmin):
    list_display = ('name_link', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)
    inlines = [ScheduleDelayLine]
    extra = 0

    name_link = MigasFields.link(model=Schedule, name='name')

    def get_queryset(self, request):
        self.request = request

        return super(ScheduleAdmin, self).get_queryset(
            request
        )

@admin.register(Store)
class StoreAdmin(MigasAdmin):
    form = StoreForm
    list_display = ('name_link', 'project_link')
    search_fields = ('name',)
    list_filter = (('project', ProjectFilterAdmin),)
    ordering = ('name',)

    fieldsets = (
        ('', {
            'fields': (
                'name',
                'project',
            )
        }),
    )

    name_link = MigasFields.link(model=Store, name='name')
    project_link = MigasFields.link(
        model=Store, name='project', order='project__name'
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(StoreAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        return super(StoreAdmin, self).get_queryset(
            request
        ).select_related("project")


@admin.register(ServerAttribute)
class ServerAttributeAdmin(MigasAdmin):
    form = ServerAttributeForm
    list_display = (
        'value_link', 'description', 'total_computers', 'property_link'
    )
    list_select_related = ('property_att',)
    fields = ('property_att', 'value', 'description', 'computers', 'inflicted_computers')
    list_filter = (ServerAttributeFilter,)
    ordering = ('property_att', 'value',)
    search_fields = ('value', 'description')
    readonly_fields = ('inflicted_computers',)

    property_link = MigasFields.link(
        model=ServerAttribute,
        name='property_att',
        order='property_att__name',
        description=_('Tag Category')
    )
    value_link = MigasFields.link(model=ServerAttribute, name='value')

    resource_class = AttributeResource

    def get_queryset(self, request):
        sql = Attribute.TOTAL_COMPUTER_QUERY
        user = request.user.userprofile
        if not user.is_view_all():
            computers = user.get_computers()
            if computers:
                sql += " AND server_computer_sync_attributes.computer_id in " \
                    + "(" + ",".join(str(x) for x in computers) + ")"
        return ServerAttribute.objects.scope(user).extra(
            select={'total_computers': sql}
        )

    def inflicted_computers(self, obj):
        ret = [
            c.link() for c in Computer.productive.filter(
                sync_attributes__in=[obj.pk]
            ).exclude(tags__in=[obj.pk])
        ]

        return format_html('<br />'.join(ret))

    inflicted_computers.short_description = _('Inflicted Computers')


@admin.register(UserProfile)
class UserProfileAdmin(MigasAdmin):
    form = UserProfileForm
    list_display = ('name_link', 'first_name', 'last_name', 'domain_link')
    ordering = ('username',)
    search_fields = ('username', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (_('General'), {
            'fields': (
                'username',
                'first_name',
                'last_name',
                'email',
                'date_joined',
                'last_login',
            ),
        }),
        (_('Authorizations'), {
            'fields': (
                'is_active',
                'is_superuser',
                'is_staff',
                'groups',
                'user_permissions',
                'domains',
            ),
        }),
        (_('Preferences'), {
            'fields': (
                'domain_preference',
                'scope_preference',
            ),
        }),
    )

    name_link = MigasFields.link(model=UserProfile, name='username')
    domain_link = MigasFields.link(model=Domain, name='domain_preference__name')


@admin.register(Scope)
class ScopeAdmin(MigasAdmin):
    form = ScopeForm
    list_display = ('name_link', 'domain_link', 'included_attributes_link', 'excluded_attributes_link')
    ordering = ('name',)
    search_fields = ('name',)
    fieldsets = (
        (_('General'), {
            'fields': (
                'name',
                'domain'
            ),
        }),
        (_('Attributes'), {
            'fields': (
                'included_attributes',
                'excluded_attributes',
            ),
        }),
        ('', {
            'fields': ('user',),
            'classes': ['hidden'],
        })
    )

    name_link = MigasFields.link(model=Scope, name='name')
    domain_link = MigasFields.link(model=Domain, name='domain__name')
    included_attributes_link = MigasFields.objects_link(
        model=AttributeSet, name="included_attributes", description=_('included attributes')
    )
    excluded_attributes_link = MigasFields.objects_link(
        model=AttributeSet, name='excluded_attributes', description=_('excluded attributes')
    )

    def get_queryset(self, request):
        qs = Attribute.objects.scope(request.user.userprofile)
        return super(ScopeAdmin, self).get_queryset(
            request
        ).prefetch_related(
            Prefetch('included_attributes', queryset=qs),
            'included_attributes__property_att',
            Prefetch('excluded_attributes', queryset=qs),
            'excluded_attributes__property_att'
        )


@admin.register(Domain)
class DomainAdmin(MigasAdmin):
    form = DomainForm
    list_display = ('name_link', 'included_attributes_link', 'excluded_attributes_link')
    ordering = ('name',)
    search_fields = ('name',)
    fieldsets = (
        (_('General'), {
            'fields': (
                'name', 'comment',
            ),
        }),
        (_('Attributes'), {
            'fields': (
                'included_attributes',
                'excluded_attributes',
             ),
        }),
        (_('Available tags'), {
            'fields': (
                'tags',
            ),
        }),
    )

    name_link = MigasFields.link(model=Domain, name='name')
    included_attributes_link = MigasFields.objects_link(
        model=AttributeSet, name="included_attributes", description=_('included attributes')
    )
    excluded_attributes_link = MigasFields.objects_link(
        model=AttributeSet, name='excluded_attributes', description=_('excluded attributes')
    )

    def get_queryset(self, request):
        user_profile = UserProfile.objects.get(id=request.user.id)
        user_profile.update_scope(0)
        return super(DomainAdmin, self).get_queryset(request)


@admin.register(Project)
class ProjectAdmin(MigasAdmin):
    list_display = (
        'name_link',
        'platform_link',
        'pms_link',
        'my_auto_register_computers'
    )
    fields = ('name', 'platform', 'pms', 'auto_register_computers')
    list_filter = (('platform', PlatformFilterAdmin), 'pms')
    list_select_related = ('platform', 'pms')
    search_fields = ('name',)
    actions = None

    name_link = MigasFields.link(model=Project, name='name')
    platform_link = MigasFields.link(
        model=Project, name='platform', order='platform__name'
    )
    pms_link = MigasFields.link(model=Project, name='pms', order='pms__name')
    my_auto_register_computers = MigasFields.boolean(
        model=Project, name='auto_register_computers'
    )

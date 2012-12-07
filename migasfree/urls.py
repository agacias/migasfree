# -*- coding: utf-8 -*-

"""
set up our URLs
"""

import os
import settings

from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()

from migasfree.server.views import *
from ajax_select import urls as ajax_select_urls

urlpatterns = patterns(
    '',
    # Example:
    # (r'^migasfree/', include('migasfree.migasfree.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^migasfree/doc/', include('django.contrib.admindocs.urls')),

    url(r'^migasfree/admin/lookups/', include(ajax_select_urls)),

    # Uncomment the next line to enable the admin:
    url(r'^migasfree/admin/', include(admin.site.urls)),

    # (r'^migasfree/jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
    # (r'^migasfree/jsi18n', 'django.views.i18n.javascript_catalog'),

    # migasfree.server.urls
    url(
        r'^$',
        redirect_to,
        {'url': '/migasfree/main/'},
        name='bootstrap'
    ),

    url(
        r'^migasfree/$',
        redirect_to,
        {'url': '/migasfree/main/'},
    ),

    url(r'^ajax_status/$', ajax_status, name='ajax_status'),
    url(r'^ajax_status_list/$', ajax_status_list, name='ajax_status_list'),
    url(r'^migasfree/main/$', main, name='dashboard'),
    url(r'^migasfree/query/(?P<query_id>\d+)/$', query, name='query'),
    url(r'^migasfree/queryMessage/$', query_message, name='computer_messages'),
    url(
        r'^migasfree/queryMessageServer/$',
        query_message_server,
        name="server_messages"
    ),

    url(r'^migasfree/info/(.*)', info, name='package_info'),

    url(
        r'^migasfree/version/$',
        change_version,
        name='change_version'
    ),

    url(r'^accounts/login/$', login, name='login'),

    url(r'^migasfree/createrepositories/$',
        createrepositories,
        name='createrepositories'
    ),

    (r'^migasfree/device/(.*)', device),

    url(r'^migasfree/chart/(?P<chart_type>.*)/$', chart, name='chart_type'),
    url(
        r'^migasfree/hourly_updated/$',
        hourly_updated,
        name='chart_hourly_updated'
    ),
    url(
        r'^migasfree/daily_updated/$',
        daily_updated,
        name='chart_daily_updated'
    ),
    url(
        r'^migasfree/monthly_updated/$',
        monthly_updated,
        name='chart_monthly_updated'
    ),
    url(
        r'^migasfree/delaySchedule/$',
        delay_schedule,
        name='chart_delay_schedule'
    ),
    url(
        r'^migasfree/version_Computer/$',
        version_computer,
        name='chart_version_computer'
    ),

    url(
        r'^migasfree/hardware/(.*)',
        hardware,
        name='hardware'
    ),
    url(
        r'^migasfree/hardware_resume/(.*)',
        hardware_resume,
        name='hardware_resume'
    ),

    # migasfree.api.urls
    # (r'^migasfree/get_device/(.*)', get_device),

    (r'^migasfree/api/$', api),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^repo/(?P<path>.*)$', 'serve', {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': True
        }),

        (r'^media/(?P<path>.*)$', 'serve', {
            'document_root': os.path.join(os.path.dirname(__file__), 'media'),
            'show_indexes': True
        }),
    )

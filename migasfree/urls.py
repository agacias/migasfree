# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog

from ajax_select import urls as ajax_select_urls
from rest_framework.authtoken import views
from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view

from .server.routers import router, device_router
from .catalog.routers import router as catalog_router
from .stats.routers import router as stats_router

from django.contrib import admin
admin.autodiscover()

TITLE = 'Migasfree REST API'

swagger_schema_view = get_swagger_view(title=TITLE)

urlpatterns = [
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^docs/', swagger_schema_view, name='docs'),
    url(r'^api-docs/', include_docs_urls(title=TITLE)),
    url(r'^token-auth/$', views.obtain_auth_token),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^api/v1/token/', include(router.urls)),
    url(r'^api/v1/token/', include(stats_router.urls)),
    url(r'^api/v1/token/devices/', include(device_router.urls)),
    url(r'^api/v1/token/catalog/', include(catalog_router.urls)),

    url(r'', include('migasfree.server.urls')),
    url(r'', include('migasfree.stats.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),

    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^markdownx/', include('markdownx.urls')),

    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

    if settings.STATIC_ROOT is not None:
        urlpatterns += static(
            settings.STATIC_URL,
            document_root=settings.STATIC_ROOT
        )

    if settings.MEDIA_ROOT is not None:
        urlpatterns += static(
            settings.MEDIA_URL,
            document_root=settings.MEDIA_ROOT,
            show_indexes=True
        )

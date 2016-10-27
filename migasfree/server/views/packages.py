# -*- coding: utf-8 -*-

import os

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from ..models import Version, UserProfile
from ..functions import run_in_server

import logging
logger = logging.getLogger('migasfree')


@login_required
def info(request, path=None):
    version_name = ''
    package = ''

    if path:
        try:
            version_name, package = path.split('/', 1)
        except ValueError:
            version_name = path

    logger.debug('package: ' + package)

    absolute_path = os.path.join(settings.MIGASFREE_REPO_DIR, path)
    logger.debug('absolute path:' + absolute_path)

    if os.path.isfile(absolute_path):
        version = get_object_or_404(Version, name=version_name)
        logger.debug('version: ' + version_name)

        cmd = 'PACKAGE={}\n'.format(absolute_path)
        cmd += version.pms.info
        package_info = run_in_server(cmd)["out"]

        return render(
            request,
            'package_info.html',
            {
                'title': '%s: %s' % (_("Package Information"), package.split('/')[-1]),
                'package_info': package_info,
            }
        )

    if os.path.isdir(absolute_path):
        file_selection = []
        if path:
            file_selection.append({
                'icon': 'folder', 'path': path + '..', 'text': '..'
            })

        elements = os.listdir(absolute_path)
        elements.sort()
        for item in elements:
            icon = 'archive'
            relative_path = os.path.join(path, item)

            if os.path.isdir(os.path.join(absolute_path, item)):
                icon = 'folder'
                relative_path += '/'  # navigation: folders always with trailing slash!!

                if not package:  # first level of navigation
                    if item in ['errors']:  # no navigation in several folders
                        continue

            file_selection.append({
                'icon': icon, 'path': relative_path, 'text': item
            })

        logger.debug('content:' + str(file_selection))

        return render(
            request,
            'package_info.html',
            {
                'title': _("Package Information"),
                'file_selection': file_selection,
            }
        )

    return render(
        request,
        'error.html',
        {
            'description': _('Error'),
            'contentpage': '%s: %s' % (_('No package information exists'), package),
        }
    )


@login_required
def change_version(request):
    if request.method == 'GET':
        version = get_object_or_404(Version, pk=request.GET.get('version'))

        user_profile = UserProfile.objects.get(id=request.user.id)
        user_profile.update_version(version)

    next_page = request.META.get('HTTP_REFERER', reverse('bootstrap'))
    if next_page.find(reverse('admin:server_repository_changelist')) > 0:
        next_page = '%s?active__exact=1' \
            % reverse('admin:server_repository_changelist')

    return HttpResponseRedirect(next_page)

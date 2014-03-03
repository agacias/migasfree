# -*- coding: UTF-8 -*-

import os
import sys
import errno
import tempfile

import django

from datetime import timedelta

from django.utils.translation import ugettext_lazy as _

from migasfree.settings import DATABASES, MIGASFREE_APP_DIR, \
    MIGASFREE_REPO_DIR, MIGASFREE_INVALID_UUID


def is_db_sqlite():
    return DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'


def config_apache():
    _apache_path = ''
    if os.path.exists('/etc/apache/conf.d'):
        _apache_path = '/etc/apache/conf.d'
    elif os.path.exists('/etc/apache2/conf.d'):
        _apache_path = '/etc/apache2/conf.d'
    elif os.path.exists('/etc/httpd/conf.d'):
        _apache_path = '/etc/httpd/conf.d'

    if not _apache_path:
        print('Apache path not found.')
        sys.exit(errno.ENOTDIR)

    # FIXME VirtualHost
    _config = \
"""
Alias /static/ajax_select %(migasfree_app_dir)s/../ajax_select/static/ajax_select
Alias /static/admin/css/admin-inlines.css %(migasfree_app_dir)s/admin_bootstrapped/static/admin/css/admin-inlines.css
Alias /static/admin/css/overrides.css %(migasfree_app_dir)s/admin_bootstrapped/static/admin/css/overrides.css
Alias /static/admin/js/generic-lookup.js %(migasfree_app_dir)s/admin_bootstrapped/static/admin/js/generic-lookup.js
Alias /static/admin/js/jquery.sortable.js %(migasfree_app_dir)s/admin_bootstrapped/static/admin/js/jquery.sortable.js
Alias /static/js/jquery.min.js %(migasfree_app_dir)s/admin_bootstrapped/static/js/jquery.min.js
Alias /static/js/jquery-ui.min.js %(migasfree_app_dir)s/admin_bootstrapped/static/js/jquery-ui.min.js
Alias /static/admin %(django_dir)s/contrib/admin/static/admin
Alias /static/bootstrap %(migasfree_app_dir)s/admin_bootstrapped/static/bootstrap
Alias /static/flot %(migasfree_app_dir)s/flot/static/flot
Alias /static %(migasfree_app_dir)s/server/static
Alias /repo %(migasfree_repo_dir)s
<Directory %(migasfree_repo_dir)s>
    Order allow,deny
    Options Indexes FollowSymlinks
    Allow from all
    IndexOptions FancyIndexing
</Directory>

WSGIScriptAlias / %(migasfree_app_dir)s/wsgi.py
"""

    _filename = os.path.join(_apache_path, 'migasfree.conf')
    _write_web_config(_filename, _config)


def _write_web_config(filename, config):
    _content = config % {
        'django_dir': os.path.dirname(os.path.abspath(django.__file__)),
        'migasfree_repo_dir': MIGASFREE_REPO_DIR,
        'migasfree_app_dir': MIGASFREE_APP_DIR
    }

    if not writefile(filename, _content):
        print('Problem found creating web server configuration file.')
        sys.exit(errno.EINPROGRESS)


def trans(string):
    return unicode(_(string))  # pylint: disable-msg=E1102


def writefile(filename, content):
    '''
    bool writefile(string filename, string content)
    '''

    _file = None
    try:
        _file = open(filename, 'wb')
        _file.write(content)
        _file.flush()
        os.fsync(_file.fileno())
        _file.close()

        return True
    except IOError:
        return False
    finally:
        if _file is not None:
            _file.close()


def readfile(filename):
    with open(filename, 'rb') as fp:
        ret = fp.read()

    return ret


def l2s(lst):
    """
    list to string
    """
    return lst.__str__()


def s2l(cad):
    """
    string to list
    """
    lst = []
    if str(cad) == "None":
        return lst
    try:
        lst = eval(cad)
        return lst
    except:
        return lst


def vl2s(field):
    """
    value_list("id") to string
    """
    return str(field.values_list("id")).replace("(", "").replace(",)", "")


class Mmcheck():
    field = None  # is a ManyToManyField
    field_copy = None  # is a Text Field

    def __init__(self, field, field_copy):
        self.field = field
        self.field_copy = field_copy

    def mms(self):
        return vl2s(self.field)

    def changed(self):
        return not self.mms() == str(self.field_copy)


def horizon(mydate, delay):
    """
    No weekends
    """
    iday = int(mydate.strftime("%w"))
    idelta = delay + (((delay + iday - 1) / 5) * 2)

    return mydate + timedelta(days=idelta)


def compare_values(val1, val2):
    if len(val1) != len(val2):
        return False

    for x in val1:
        if not x in val2:
            return False

    return True


def list_difference(list1, list2):
    """uses list1 as the reference, returns list of items not in list2"""
    diff_list = []
    for item in list1:
        if not item in list2:
            diff_list.append(item)

    return diff_list


def list_common(list1, list2):
    """uses list1 as the reference, returns list of items in list2"""
    diff_list = []
    for item in list1:
        if item in list2:
            diff_list.append(item)

    return diff_list


def old_new_elements(list1, list2):
    """Given two lists returns a list with the old elements
    and other list with the new elements"""
    return (
        list_difference(list1, list2),
        list_difference(list2, list1)
    )


def run_in_server(code_bash):
    _, tmp_file = tempfile.mkstemp()
    writefile(tmp_file, code_bash)

    os.system("bash %(file)s 1> %(file)s.out 2> %(file)s.err" % {
        'file': tmp_file
    })

    out = readfile('%s.out' % tmp_file)
    err = readfile('%s.err' % tmp_file)

    os.remove(tmp_file)
    os.remove('%s.out' % tmp_file)
    os.remove('%s.err' % tmp_file)

    return {"out": out, "err": err}


def get_client_ip(request):
    ip = request.META.get('REMOTE_ADDR')

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]

    return ip


def uuid_validate(uuid):
    if len(uuid) == 32:
        uuid = "%s-%s-%s-%s-%s" % (
            uuid[0:8],
            uuid[8:12],
            uuid[12:16],
            uuid[16:20],
            uuid[20:32]
        )

    if uuid in MIGASFREE_INVALID_UUID:
        return ""
    else:
        return uuid

def uuid_change_format(uuid):
    """
    change to big-endian or little-endian format
    """
    if len(uuid) == 36:
        return "%s%s%s%s-%s%s-%s%s-%s-%s" % (
                uuid[6:8],
                uuid[4:6],
                uuid[2:4],
                uuid[0:2],
                uuid[11:13],
                uuid[9:11],
                uuid[16:18],
                uuid[14:16],
                uuid[19:23],
                uuid[24:36])
    return uuid


def add_default_device_logical(device):
    from migasfree.server.models import DeviceFeature, DeviceLogical

    for feature in DeviceFeature.objects.all().filter(
        devicedriver__model=device.model
    ).distinct():
        logical = DeviceLogical()
        logical.device = device
        logical.feature = feature
        logical.save()

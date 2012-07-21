# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

import sys

from django.conf import settings
from django.db.models.loading import cache
from django.db.models.signals import post_syncdb
from django.utils.datastructures import SortedDict


def escape_schema_name(name):
    """ Escape system names for PostgreSQL. Should do the trick. """
    return name.replace('"', '""')


def get_apps():
    """
    Returns a tupple of shared and isolated apps. If south is in
    INSTALLED_APPS, if will always be in both lists.

    Obviously, appschema cannot be in isolated apps.
    """
    all_apps = list(settings.INSTALLED_APPS)
    shared_apps = list(settings.APPSCHEMA_SHARED_APPS)
    both_apps = list(settings.APPSCHEMA_BOTH_APPS)

    # South models should be shared and isolated
    if 'south' in all_apps and 'south' not in both_apps:
        both_apps.append('south')

    # Appschema cannot be isolated
    if 'appschema' not in shared_apps:
        shared_apps.append('appschema')

    #isolated = [app for app in all_apps if app not in shared_apps]

    isolated = [x for x in all_apps if x not in shared_apps or x in both_apps]
    shared = [x for x in all_apps if x in shared_apps or x in both_apps]

    return shared, isolated


def load_post_syncdb_signals():
    """
    This is a duplicate from Django syncdb management command.

    This code imports any module named 'management' in INSTALLED_APPS.
    The 'management' module is the preferred way of listening to post_syncdb
    signals.
    """
    unload_post_syncdb_signals()

    # If south is available, we should reload it's post_migrate signal.
    try:
        import south.signals
        south.signals.post_migrate.receivers = []
        #reload(south.signals)
    except ImportError:
        pass

    for app_name in settings.INSTALLED_APPS:
        try:
            module = app_name + '.management'

            # As we first unload signals, we need to reload module
            # if present in modules cache. That will reload signals.
            if sys.modules.get(module):
                reload(sys.modules[module])
            else:
                __import__(module, {}, {}, [''])

        except ImportError, exc:
            msg = exc.args[0]
            if not msg.startswith('No module named') or 'management' not in msg:
                raise


def unload_post_syncdb_signals():
    """
    This function disconnects ALL post_syncdb signals. This is needed by
    some tricky migration and syncdb behaviors and when you isolate apps
    like contenttypes or auth (which is often the case).
    """
    post_syncdb.receivers = []


def get_app_label(app):
    """ Returns app label as Django make it. """
    return '.'.join(app.__name__.split('.')[0:-1])


def run_with_apps(apps, func, *args, **kwargs):
    """
    This function is a wrapper to any function that will change INSTALLED_APPS
    and Django cache.app_store.
    Both variables are reset after function execution.
    """
    old_installed, settings.INSTALLED_APPS = settings.INSTALLED_APPS, apps

    old_app_store, cache.app_store = cache.app_store, SortedDict([
        (k, v) for (k, v) in cache.app_store.items()
        if get_app_label(k) in apps
    ])

    try:
        return func(apps, *args, **kwargs)
    finally:
        settings.INSTALLED_APPS = old_installed
        cache.app_store = old_app_store

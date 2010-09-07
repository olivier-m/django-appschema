# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

from django.core.exceptions import ImproperlyConfigured

try:
    from south.exceptions import NoMigrations
    from south.migration import Migrations
    south_ok = True
except ImportError:
    south_ok = False

def get_migration_candidates(apps):
    """
    This function returns only apps that could be migrated.
    """
    res = []
    if not south_ok:
        return res
    
    for app in apps:
        try:
            Migrations(app)
            res.append(app)
        except (NoMigrations, ImproperlyConfigured):
            pass
    
    return res

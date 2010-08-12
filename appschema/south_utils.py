# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

from django.core.exceptions import ImproperlyConfigured

from south.exceptions import NoMigrations
from south.migration import Migrations

def get_migration_candidates(apps):
    """
    This function returns only apps that could be migrated.
    """
    res = []
    for app in apps:
        try:
            Migrations(app)
            res.append(app)
        except (NoMigrations, ImproperlyConfigured):
            pass
    
    return res

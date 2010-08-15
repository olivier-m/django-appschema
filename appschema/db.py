# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

from appschema import syncdb, migrate
syncdb = syncdb()
migrate = migrate()

from appschema.schema import schema_store
from appschema.utils import get_apps, load_post_syncdb_signals, run_with_apps

def syncdb_apps(apps, schema=None, **options):
    """
    This function simply call syncdb command (Django or South one) for
    select apps only.
    """
    def wrapper(_apps, *args, **kwargs):
        load_post_syncdb_signals()
        return syncdb.Command().execute(**kwargs)
    
    # Syncdb without schema (on public)
    if not schema:
        schema_store.reset_path()
        return run_with_apps(apps, wrapper, **options)
    
    # Syncdb with schema
    #
    # We first handle the case of apps that are both shared and isolated.
    # As this tables are already present in public schema, we can't sync
    # with a search_path <schema>,public
    
    shared_apps, _ = get_apps()
    both_apps = [x for x in apps if x in shared_apps]
    shared_apps = [x for x in apps if x not in both_apps]
    
    schema_store.schema = schema
    
    if 'south' in apps:
        try:
            schema_store.force_path()
            run_with_apps(both_apps, wrapper, **options)
        except ValueError:
            pass
    
    try:
        # For other apps, we work with seach_path <schema>,public to
        # properly handle cross schema foreign keys.
        schema_store.set_path()
        run_with_apps(shared_apps, wrapper, **options)
    finally:
        schema_store.clear()

def migrate_apps(apps, schema=None, **options):
    def wrapper(_apps, *args, **kwargs):
        load_post_syncdb_signals()
        for _app in _apps:
            migrate.Command().execute(_app, **kwargs)
    
    # Migrate without schema (on public)
    if not schema:
        schema_store.reset_path()
        run_with_apps(apps, wrapper, **options)
        return
    
    # Migrate with schema
    schema_store.schema = schema
    
    try:
        # For other apps, we work with seach_path <schema>,public to
        # properly handle cross schema foreign keys.
        schema_store.set_path()
        run_with_apps(apps, wrapper, **options)
    finally:
        schema_store.clear()
    

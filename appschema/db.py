# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.
from multiprocessing import Process

from django import db

import appschema
syncdb = appschema.syncdb()
migrate = appschema.migrate()

from appschema.schema import schema_store
from appschema.utils import get_apps, load_post_syncdb_signals, run_with_apps


def _syncdb_apps(apps, schema=None, **options):
    """
    This function simply call syncdb command (Django or South one) for
    select apps only.
    """
    def wrapper(_apps, *args, **kwargs):
        load_post_syncdb_signals()
        return syncdb.Command().execute(**kwargs)

    # Force connection close
    db.connection.close()
    db.connection.connection = None

    # Force default DB if not specified
    options['database'] = options.get('database', db.DEFAULT_DB_ALIAS)

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


def _migrate_apps(apps, schema=None, **options):
    def wrapper(_apps, *args, **kwargs):
        load_post_syncdb_signals()
        for _app in _apps:
            migrate.Command().execute(_app, **kwargs)

    # Force connection close
    db.connection.close()
    db.connection.connection = None

    # Force default DB if not specified
    options['database'] = options.get('database', db.DEFAULT_DB_ALIAS)

    # Migrate without schema (on public)
    if not schema:
        schema_store.reset_path()
        run_with_apps(apps, wrapper, **options)
        return

    # Migrate with schema
    schema_store.schema = schema

    if len(db.connections.databases) > 1:
        raise Exception('Appschema doest not support multi databases (yet?)')

    try:
        # For other apps, we work with seach_path <schema>,public to
        # properly handle cross schema foreign keys.
        schema_store.set_path()

        # South sometimes needs a schema settings to be set and take it from
        # Django db settings SCHEMA
        db.connection.settings_dict['SCHEMA'] = schema

        run_with_apps(apps, wrapper, **options)
    finally:
        schema_store.clear()
        if 'SCHEMA' in db.connection.settings_dict:
            del db.connection.settings_dict['SCHEMA']


def syncdb_apps(apps, schema=None, **options):
    p = Process(target=_syncdb_apps, args=(apps, schema), kwargs=options)
    p.start()
    p.join()
    p.terminate()
    if p.exitcode != 0:
        raise RuntimeError('Unexpected end of subprocess')


def migrate_apps(apps, schema=None, **options):
    p = Process(target=_migrate_apps, args=(apps, schema), kwargs=options)
    p.start()
    p.join()
    if p.exitcode != 0:
        raise RuntimeError('Unexpected end of subprocess')

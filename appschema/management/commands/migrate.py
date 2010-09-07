# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from south.db import DEFAULT_DB_ALIAS

import appschema
migrate = appschema.migrate()

from appschema.db import migrate_apps
from appschema.models import Schema
from appschema.south_utils import get_migration_candidates
from appschema.utils import get_apps, load_post_syncdb_signals

class Command(BaseCommand):
    option_list = migrate.Command.option_list
    help = migrate.Command.help
    args = migrate.Command.args
    
    def handle(self, app=None, target=None, skip=False, merge=False,
    backwards=False, fake=False, db_dry_run=False, show_list=False,
    database=DEFAULT_DB_ALIAS, delete_ghosts=False, ignore_ghosts=False,
    **options):
        if not 'south' in settings.INSTALLED_APPS:
            raise CommandError('South is not installed.')
        
        verbosity = int(options.get('verbosity', 0))
        shared, isolated = get_apps()
        
        if options.get('all_apps', False):
            target = app
            app = None
        
        # Migrate each app
        if app:
            apps = [app]
        else:
            apps = settings.INSTALLED_APPS
        
        options.update({
            'target': target,
            'skip': skip,
            'merge': merge,
            'backwards': backwards,
            'fake': fake,
            'db_dry_run': db_dry_run,
            'show_list': show_list,
            'database': database,
            'delete_ghosts': delete_ghosts,
            'ignore_ghosts': ignore_ghosts
        })
        
        shared_apps = [x for x in get_migration_candidates(shared) if x in apps]
        isolated_apps = [x for x in get_migration_candidates(isolated) if x in apps]
        
        try:
            if len(shared_apps) > 0:
                if verbosity:
                    print "---------------------"
                    print "SHARED APPS migration"
                    print "---------------------\n"
                
                migrate_apps(shared_apps, None, **options)
            
            if len(isolated_apps) == 0:
                return
            
            for schema in Schema.objects.active():
                if verbosity:
                    print "\n----------------------------------"
                    print   "ISOLATED APPS migration on schema: %s" % schema.name
                    print   "----------------------------------\n"
                migrate_apps(isolated_apps, schema=schema.name, **options)
        finally:
            load_post_syncdb_signals()
    

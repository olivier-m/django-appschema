# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.core.management.sql import custom_sql_for_model
from django.db.models.loading import cache
from django.utils.datastructures import SortedDict

import appschema
syncdb = appschema.syncdb()

from appschema.db import syncdb_apps
from appschema.models import Schema
from appschema.utils import get_apps, load_post_syncdb_signals

class Command(NoArgsCommand):
    option_list = syncdb.Command.option_list
    help = syncdb.Command.help
    
    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity', 0))
        
        shared_apps, isolated_apps = get_apps()
        
        try:
            if len(shared_apps) > 0:
                if verbosity:
                    print "----------------"
                    print "SHARED APPS sync"
                    print "----------------\n"
                
                syncdb_apps(shared_apps, **options)
            
            if len(isolated_apps) == 0:
                return
            
            for schema in Schema.objects.active():
                if verbosity:
                    print "\n------------------------"
                    print   "ISOLATED APPS on schema: %s" % schema.name
                    print   "------------------------\n"
                    
                syncdb_apps(isolated_apps, schema.name, **options)
        finally:
            load_post_syncdb_signals()
        
    

# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

from django.core import management
from django.core.management.base import NoArgsCommand
from django import db

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
        migrate = options.get('migrate', False)
        options['migrate'] = False

        shared_apps, isolated_apps = get_apps()

        try:
            if len(shared_apps) > 0:
                if verbosity:
                    print "------------------"
                    print "SHARED APPS syncdb"
                    print "------------------\n"

                syncdb_apps(shared_apps, schema=None, **options)

            if len(isolated_apps) == 0:
                return

            schema_list = [x.name for x in Schema.objects.active()]
            for schema in schema_list:
                if verbosity:
                    print "\n-------------------------------"
                    print "ISOLATED APPS syncdb on schema: %s" % schema
                    print "-------------------------------\n"

                syncdb_apps(isolated_apps, schema=schema, **options)
        finally:
            load_post_syncdb_signals()

        if migrate:
            db.connection.close()
            db.connection.connection = None
            management.call_command("migrate")

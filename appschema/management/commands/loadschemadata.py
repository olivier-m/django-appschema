# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands import loaddata

from appschema.models import Schema
from appschema.schema import schema_store

class Command(BaseCommand):
    option_list = loaddata.Command.option_list + (
        make_option('--schema', action='store', dest='schema',
            default=None, help='Nominates a specific schema to load '
                'fixtures into. Defaults to all schemas.'),
    )
    help = "Fixture loader with schema support"
    args = loaddata.Command.args
    
    def handle(self, *fixture_labels, **options):
        verbosity = int(options.get('verbosity', 0))
        schema = options.get('schema', None)
        
        if schema:
            try:
                schema_list = [Schema.objects.get(name=schema)]
            except Schema.DoesNotExist, e:
                raise CommandError('Schema "%s" does not exist.' % schema)
        else:
            schema_list = Schema.objects.active()
        
        for _s in schema_list:
            if verbosity:
                print "---------------------------"
                print "Loading fixtures in schema: %s" % _s.name
                print "---------------------------\n"
            
            schema_store.schema = _s.name
            schema_store.set_path()
            loaddata.Command().execute(*fixture_labels, **options)

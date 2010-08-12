# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from appschema.models import new_schema

class Command(BaseCommand):
    help = 'Creates a new active schema'
    
    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 0))
        
        if len(args) < 2:
            raise CommandError('You should specify a name and a public name')
        
        name, public_name = args[0:2]
        
        try:
            new_schema(name, public_name, True, **options)
        except Exception, e:
            raise CommandError(str(e))
    

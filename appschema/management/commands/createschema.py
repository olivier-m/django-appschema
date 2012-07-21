# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS

from appschema.models import new_schema


class Command(BaseCommand):
    help = 'Creates a new active schema'
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to create schema on. '
                'Defaults to the "default" database.'),
    )

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError('You should specify a name and a public name')

        name, public_name = args[0:2]

        try:
            new_schema(name, public_name, True, **options)
        except Exception, e:
            raise
            raise CommandError(str(e))

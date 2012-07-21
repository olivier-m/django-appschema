# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.
from optparse import make_option
import re
from subprocess import Popen, PIPE

from django.conf import settings
from django.core.management.base import BaseCommand

import appschema
from appschema.models import create_schema, drop_schema

syncdb = appschema.syncdb()


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--pgdump', action='store', dest='pgdump',
            default='pg_dump', help='Path to pg_dump command'),
        make_option('--rawsql', action='store_true', dest='raw',
            default=False, help='Output non formatted schema dump'),
        make_option('--aspython', action='store_true', dest='as_python',
            default=False, help='Output dump in a python string.'),
        make_option('--tempname', action='store', dest='schema_name',
            default='__master__', help='Name of temporary schema')
    )

    option_list += tuple([x for x in syncdb.Command.option_list if x.dest == "database"])

    help = "Dumps the whole base schema creation and gives result on stdout."

    def handle(self, *fixture_labels, **options):
        pg_dump = options.get('pgdump')
        raw = options.get('raw', False)
        as_python = options.get('as_python', False)
        schema_name = options.get('schema_name', '__master__')

        create_schema(schema_name, **{
            'verbosity': 0,
            'database': options.get("database")
        })

        try:
            cmd = [pg_dump,
                '-n', schema_name,
                '--no-owner',
                '--inserts'
            ]

            if settings.DATABASES['default']['USER']:
                cmd.extend(['-U', settings.DATABASES['default']['USER']])

            if settings.DATABASES['default']['HOST']:
                cmd.extend(['-h', settings.DATABASES['default']['HOST']])

            cmd.append(settings.DATABASES['default']['NAME'])

            pf = Popen(cmd,
                env={'PGPASSWORD': settings.DATABASES['default']['PASSWORD']},
                stdout=PIPE
            )
            dump = pf.communicate()[0]
        finally:
            drop_schema(schema_name)

        re_comments = re.compile(r'^--.*\n', re.M)
        re_duplines = re.compile(r'^\n\n+', re.M)

        # Adding string template schema_name
        if not raw or as_python:
            dump = dump.replace('%', '%%')
            dump = dump.replace(schema_name, '%(schema_name)s')

        # A bit nicer to read
        dump = re_comments.sub('', dump)
        dump = re_duplines.sub('\n', dump)

        if as_python:
            dump = '# -*- coding: utf-8 -*-\nschema_sql = """%s"""' % dump

        print dump

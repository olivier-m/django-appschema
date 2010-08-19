# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.
from optparse import make_option
import re
from subprocess import Popen, PIPE

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from appschema.models import new_schema, drop_schema

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--pgdump', action='store', dest='pgdump',
            default='pg_dump', help='Path to pg_dump command'),
        make_option('--rawsql', action='store_true', dest='raw',
            default=False, help='Output non formatted schema dump'),
        make_option('--aspython', action='store_true', dest='as_python',
            default=False, help='Output dump in a python string.'),
    )
    help = "Dumps the whole base schema creation and gives result on stdout."
    
    def handle(self, *fixture_labels, **options):
        verbosity = int(options.get('verbosity', 0))
        pg_dump = options.get('pgdump')
        raw = options.get('raw', False)
        as_python = options.get('as_python', False)
        
        schema_name = '__master__'
        
        new_schema(schema_name, schema_name, False, **{'verbosity': 0})
        
        pf = Popen(
            [pg_dump,
                '-n', schema_name,
                '--no-owner',
                '--inserts',
                settings.DATABASES['default']['NAME']
            ],
            env={'PGPASSWORD': settings.DATABASES['default']['PASSWORD']},
            stdout=PIPE
        )
        
        dump = pf.communicate()[0]
        drop_schema(schema_name)
        
        re_comments = re.compile(r'^--.*\n', re.M)
        re_duplines = re.compile(r'^\n\n', re.M)
        
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
    

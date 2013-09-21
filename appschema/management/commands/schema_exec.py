# -*- coding: utf-8 -*-
import os.path
import sys

from django.db import connections, DEFAULT_DB_ALIAS

from appschema.models import Schema
from appschema.schema import schema_store

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Execute given SQL file on every schema'
    args = '<sql-file>'

    def handle(self, *args, **kwargs):
        if len(args) == 0:
            raise CommandError('No SQL file specified')

        filename = args[0]
        if not os.path.exists(filename):
            raise CommandError('File "%s" does not exist.' % filename)

        with open(filename, 'rb') as fp:
            sql = fp.read()

        for instance in Schema.objects.all():
            schema_store.reset_path()
            schema_store.schema = instance.name
            schema_store.force_path()

            sys.stdout.write('%s ... ' % instance.name)
            try:
                cur = connections[DEFAULT_DB_ALIAS].cursor()
                cur.execute(sql)
                cur.close()
                sys.stdout.write(self.style.SQL_COLTYPE('✓'))
                sys.stdout.write('\n')
            except:
                sys.stdout.write(self.style.NOTICE('✗'))
                sys.stdout.write('\n')
                raise

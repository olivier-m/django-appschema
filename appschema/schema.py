# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

from django.conf import settings
from django.db import connection, models, transaction

__all__ = ('schema_store',)

def get_path(*args):
    path = ['"%s"' % x for x in list(args) + list(settings.APPSCHEMA_DEFAULT_PATH)]
    return ','.join(path)

from threading import local
class SchemaStore(local):
    """
    A simple thread safe store that will set search_path when asked for.
    """
    def __init__(self):
        self.clear()
    
    def clear(self):
        self._schema = None
    
    def get_schema(self):
        return self._schema
    
    def set_schema(self, value):
        self._schema = value
    
    schema = property(get_schema, set_schema)
    
    def set_path(self, cursor=None):
        cursor = cursor or connection.cursor()
        args = self.schema and [self.schema] or []
        cursor.execute('SET search_path = %s' % get_path(*args))
    
    def force_path(self, cursor=None):
        cursor = cursor or connection.cursor()
        cursor.execute('SET search_path = "%s"' % self.schema)
    
    def reset_path(self, cursor=None):
        self.clear()
        self.set_path(cursor)
    

schema_store = SchemaStore()

# On every connection, we set the schema in store
from django.db.backends import signals
def set_schema(sender, **kwargs):
    schema_store.set_path()

signals.connection_created.connect(set_schema)
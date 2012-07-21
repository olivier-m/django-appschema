# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

from django.conf import settings
from django.http import Http404, HttpResponseRedirect

from appschema.schema import schema_store
from appschema.models import Schema


class NoSchemaError(Http404):
    pass


class FqdnMiddleware(object):
    """
    This Middleware sets schema based on FQDN.
    FQDN should be the public_name in your schema table.
    """
    def should_process(self, request):
        if not settings.DEBUG:
            return True

        if getattr(settings, 'MEDIA_URL') and request.path.startswith(settings.MEDIA_URL):
            return False

        if request.path == '/favicon.ico':
            return False

        return True

    def get_schema_name(self, fqdn):
        try:
            schema = Schema.objects.get(public_name=fqdn, is_active=True)
            schema_store.schema = schema.name
            schema_store.set_path()
            return True
        except Schema.DoesNotExist:
            raise NoSchemaError()

    def process_request(self, request):
        if self.should_process(request):
            fqdn = request.get_host().split(':')[0]
            try:
                self.get_schema_name(fqdn)
            except NoSchemaError:
                if hasattr(settings, 'APPSCHEMA_SCHEMA_REDIRECT'):
                    return HttpResponseRedirect(settings.APPSCHEMA_SCHEMA_REDIRECT)
                raise

    def process_response(self, request, response):
        if self.should_process(request):
            schema_store.clear()

        return response

    def process_exception(self, request, exception):
        if self.should_process(request):
            schema_store.clear()

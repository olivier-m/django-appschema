# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

from django.conf import settings

from django.conf import settings

if not hasattr(settings, 'APPSCHEMA_SHARED_APPS'):
    settings.APPSCHEMA_SHARED_APPS = ()

if not hasattr(settings, 'APPSCHEMA_DEFAULT_PATH'):
    settings.APPSCHEMA_DEFAULT_PATH = ['public']

if not hasattr(settings, 'APPSCHEMA_BOTH_APPS'):
    settings.APPSCHEMA_BOTH_APPS = ()

def syncdb():
    """ Returns good syncdb module based on installed apps """
    if 'south' in settings.INSTALLED_APPS:
        module = 'south.management.commands'
    else:
        module = 'django.core.management.commands'
    
    module = __import__(module + '.syncdb', {}, {}, [''])
    
    return module

def migrate():
    """ Returns South migrate command if South is installed """
    if not 'south' in settings.INSTALLED_APPS:
        return None
    
    module = __import__('south.management.commands', globals(), locals(), ['migrate'], -1)
    return module.migrate


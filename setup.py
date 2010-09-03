# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.

from setuptools import setup, find_packages

version = '0.4'
packages = ['appschema'] + ['appschema.%s' % x for x in find_packages('appschema',)]

setup(
    name='appschema',
    version=version,
    description='SaaS helper that isolates django apps in schemas.',
    author='Olivier Meunier',
    author_email='om@neokraft.net',
    url='http://bitbucket.org/cedarlab/django-appschema/',
    packages=packages,
    classifiers=[
        'Development Status :: %s' % version,
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)

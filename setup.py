# -*- coding: utf-8 -*-
#
# This file is part of Django appschema released under the MIT license.
# See the LICENSE for more information.
from setuptools import setup, find_packages

execfile('appschema/version.py')

packages = find_packages(exclude=['*.tests'])

def readme():
    with open('README.rst', 'r') as fp:
        return fp.read()


setup(
    name='appschema',
    version=__version__,
    description='SaaS helper that isolates django apps in schemas.',
    long_description=readme(),
    author='Olivier Meunier',
    author_email='olivier@neokraft.net',
    url='https://github.com/olivier-m/django-appschema',
    license='MIT License',
    keywords='django database schema postgresql',
    install_requires=[
        'django>=1.4',
    ],
    packages=packages,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)

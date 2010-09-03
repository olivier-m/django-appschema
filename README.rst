================
Django appschema
================

What is it?
===========

Django Appschema is born from the idea proposed by *tidbids* on `SaaS with
Django and PostgreSQL
<http://tidbids.posterous.com/saas-with-django-and-postgresql>`_ and `SaaS
with Django and PostgreSQL Schemas
<http://tidbids.posterous.com/saas-with-django-and-postgresql-schemas>`_.

The main idea is to isolate customer's data in different schema. One customer
= one schema. There are very good explanations on why schemas and what it
could bring to your SaaS application on `this thread on Hacker News
<http://news.ycombinator.com/item?id=1565674>`_.

How it works?
=============

On the running side, schema isolation is quite easy, set up a middleware that
make dispatch, a signal and *voilà* (almost).

Django Appschema creates a table containing a ``public_name`` (could be FQDN
or whatever your middleware decides) and a associated schema. This table
should be shared by all schemas you'll create.

Now the complicated part. Performing syncdb on multiple schemas could be a bit
difficult, specially if you want to share some apps and isolate some others
(or both).

On your configuration file, you'll add ``APPSCHEMA_SHARED_APPS`` which is a
list containing the apps you want to share. Basically, shared apps tables are
created in ``public`` schema.

Appschema will alway be a shared app. If installed, South will be both shared
and isolated.

Appschema comes with modified versions of ``syncdb`` and ``migrate`` that will
perform required operations on schemas.

Another management command called ``createschema`` allows you to create a new
schema and performs syncdb (and migrate if available) on the new created
schema.

Schema creation from your web app
---------------------------------

If you look at the code, you'll find a function called ``new_schema``. You
could be tempted to use it directly in your web app (for registration
purpose). DON'T. NEVER. SERIOUSLY. In order to run properly, commands modify
INSTALLED_APPS and the Django apps cache during execution. What is not an
issue during a management command could become a nightmare in a runing Django
process.

A first solution comes with ``schematemplate`` management command. This
command creates a temporary schema, executes ``pg_dump`` on it and prints the
result on standard output. It replaces the temporary schema name by a
substitution pattern named ``%(schema_name)``. You can store this result for
later use. Runing ``schematemplate`` command on each deployment is a good
idea.

New: A function called ``new_schema_from_template`` (in ``appschema.models``)
performs the schema creation based on this template file.

Alternative: clone_schema stored procedure
------------------------------------------

Appschema provides a PostgreSQL (version 8.4 only) stored procedure called
``clone_schema(source, destination)`` (In contrib directory). It makes a copy
of ``source`` schema on ``destination``. Create a master schema and you could
use it as a source for ``clone_schema``. As this procedure is still a work in
progress, you may prefer using the ``schematemplate`` way.

Please note
===========

This **highly experimental** app works **only for PostgreSQL**.

You'll find a FqdnMiddleware which switchs schema based on the host name of
the HTTP request. Feel free to make your own based on your needs.

If you find bugs (and I'm sure you will), please report them.

It wasn't test with multiple databases support and I'm not sure it works in
such case.

Be careful with foreign keys. As you can make any foreign key you want in
isolated app models referencing shared one, the opposite is not true.

License
=======

Django appschema is released under the MIT license. See the LICENSE
file for the complete license.

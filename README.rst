django-dbtemplates
==================

.. image:: https://jazzband.co/static/img/badge.svg
   :alt: Jazzband
   :target: https://jazzband.co/

.. image:: https://github.com/mpasternak/django-dbtemplates-iplweb/workflows/Test/badge.svg
   :target: https://github.com/mpasternak/django-dbtemplates-iplweb/actions
   :alt: GitHub Actions

.. image:: https://codecov.io/github/jazzband/django-dbtemplates/coverage.svg?branch=master
   :alt: Codecov
   :target: https://codecov.io/github/jazzband/django-dbtemplates?branch=master

``dbtemplates`` is a Django app that consists of two parts:

1. It allows you to store templates in your database
2. It provides `template loader`_ that enables Django to load the
   templates from the database

It also features optional support for versioned storage and django-admin
command, integrates with Django's caching system and the admin actions.

Please see https://django-dbtemplates.readthedocs.io/ for more details.

The source code and issue tracker can be found on Github:

https://github.com/jazzband/django-dbtemplates

.. _template loader: http://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types

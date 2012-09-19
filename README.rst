django-dbtemplates
==================

.. image:: https://secure.travis-ci.org/jezdez/django-dbtemplates.png?branch=develop
    :alt: Build Status
    :target: http://travis-ci.org/jezdez/django-dbtemplates

``dbtemplates`` is a Django app that consists of two parts:

1. It allows you to store templates in your database
2. It provides `template loader`_ that enables Django to load the
   templates from the database

It also features optional support for versioned storage and django-admin
command, integrates with Django's caching system and the admin actions.

Please see http://django-dbtemplates.readthedocs.org/ for more details.

The source code and issue tracker can be found on Github:

https://github.com/jezdez/django-dbtemplates

.. _template loader: http://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
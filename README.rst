django-dbtemplates
==================

.. image:: https://secure.travis-ci.org/jazzband/django-dbtemplates.png
    :alt: Build Status
    :target: http://travis-ci.org/jazzband/django-dbtemplates

.. image:: https://jazzband.co/static/img/badge.svg
   :alt: Jazzband
   :target: https://jazzband.co/

``dbtemplates`` is a Django app that consists of two parts:

1. It allows you to store templates in your database
2. It provides `template loader`_ that enables Django to load the
   templates from the database

It also features optional support for versioned storage and django-admin
command, integrates with Django's caching system and the admin actions.

Please see https://django-dbtemplates.readthedocs.io/ for more details.

The source code and issue tracker can be found on Github:

https://github.com/jazzband/django-dbtemplates

Compatibility Roadmap
---------------------

- 1.3.2 ``dbtemplates`` dropped support for Django < 1.4
- 1.4 will be supported only Django >= 1.7, please freeze your requirements on specific version of ``dbtemplates`` !

.. _template loader: http://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types

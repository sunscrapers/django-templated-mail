=====================
django-templated-mail
=====================

.. image:: https://img.shields.io/pypi/v/django-templated-mail.svg
  :target: https://pypi.org/project/django-templated-mail

.. image:: https://img.shields.io/travis/sunscrapers/django-templated-mail.svg
  :target: https://travis-ci.org/sunscrapers/django-templated-mail

.. image:: https://img.shields.io/codecov/c/github/sunscrapers/django-templated-mail.svg
  :target: https://codecov.io/gh/sunscrapers/django-templated-mail

.. image:: https://img.shields.io/scrutinizer/g/sunscrapers/django-templated-mail.svg
  :target: https://scrutinizer-ci.com/g/sunscrapers/django-templated-mail

A simple wrapper for ``django.core.mail.EmailMultiAlternatives`` which makes
use of Django template system to store email content in separate file.

Developed by `SUNSCRAPERS <http://sunscrapers.com/>`_ with passion & patience.

Installation
============

Simply install using ``pip``:

.. code-block:: bash

    $ pip install -U django-templated-mail

Documentation
=============

Documentation is available to study at
`http://django-templated-mail.readthedocs.io <http://django-templated-mail.readthedocs.io>`_
and in ``docs`` directory.

Contributing and development
============================

To start developing on **django-templated-mail**, clone the repository:

.. code-block:: bash

    $ git clone git@github.com:sunscrapers/django-templated-mail.git

If you are a **pipenv** user you can quickly setup testing environment by
using Make commands:

.. code-block:: bash

    $ make init
    $ make test

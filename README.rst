=====================
django-templated-mail
=====================

.. image:: https://img.shields.io/pypi/v/django-templated-mail.svg
  :target: https://pypi.org/project/django-templated-mail

.. image:: https://github.com/sunscrapers/django-templated-mail/actions/workflows/test-suite.yml/badge.svg?branch=master
  :target: https://github.com/sunscrapers/django-templated-mail/actions?query=branch%3Amaster

.. image:: https://codecov.io/gh/sunscrapers/django-templated-mail/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/sunscrapers/django-templated-mail

.. image:: https://img.shields.io/pypi/dm/django-templated-mail
  :target: https://img.shields.io/pypi/dm/django-templated-mail

.. image:: https://readthedocs.org/projects/django-templated-mail/badge/?version=latest
  :target: https://django-templated-mail.readthedocs.io/en/latest/

A simple wrapper for ``django.core.mail.EmailMultiAlternatives`` which makes
use of Django template system to store email content in separate file.

Developed by `SUNSCRAPERS <http://sunscrapers.com/>`_ with passion & patience.

Requirements
============

* Python 3.9 or newer
* Django 3.2 or newer

Installation
============

Simply install using ``pip``:

.. code-block:: bash

    $ pip install -U django-templated-mail

Documentation
=============

Documentation is available to study at
`https://django-templated-mail.readthedocs.io <https://django-templated-mail.readthedocs.io>`_
and in ``docs`` directory.

Contributing and development
============================

To start developing on **django-templated-mail**, clone the repository:

.. code-block:: bash

    $ git clone git@github.com:sunscrapers/django-templated-mail.git

The project is managed with `uv <https://docs.astral.sh/uv/>`_. Set up the
environment and run the test suite with Make commands:

.. code-block:: bash

    $ make init
    $ make test

Code style is enforced with `pre-commit <https://pre-commit.com/>`_:

.. code-block:: bash

    $ make run-hooks

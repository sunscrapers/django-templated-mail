==========
Change Log
==========

This document records all notable changes to django-templated-mail.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

---------------------
`2.0.0`_ (unreleased)
---------------------

* **breaking:** drop support for Python 2.7 and 3.4-3.7; Python 3.9-3.14 are supported
* **breaking:** drop support for Django 1.11-3.1; Django 3.2-6.1 are supported
* **breaking:** ``BaseEmailMessage.send`` clears ``request`` on the instance once the
  templates have been rendered, so a sent message can be deep-copied and pickled
  (required by the locmem email backend since Django 5.1 and by task queues)
  https://github.com/sunscrapers/djoser/issues/842
* ``{{ block.super }}`` now works in email templates that extend a base template;
  previously it raised ``TemplateSyntaxError``
* add optional ``PROTOCOL`` setting, overriding the protocol derived from the
  request in the same way ``DOMAIN`` and ``SITE_NAME`` do
  https://github.com/sunscrapers/django-templated-mail/issues/31
* move packaging to ``pyproject.toml`` (hatchling) and ``uv``; drop ``setup.py``,
  ``Pipfile``, ``tox`` and Travis CI
* add GitHub Actions workflows for tests (Python x Django matrix), code quality
  (pre-commit with black, ruff, pyupgrade, docformatter) and tag-driven PyPI
  releases, mirroring djoser
* raise ``ImproperlyConfigured`` when a message has no ``template_name`` instead of
  a Django-version-dependent ``TypeError`` or ``TemplateDoesNotExist``
* fix ``BaseEmailMessage.send`` discarding Django's return value; it now returns the
  number of messages sent, like ``EmailMessage.send``
* ``BaseEmailMessage.render`` is now idempotent: a message is rendered once and
  ``send()`` reuses it. Previously ``render()`` followed by ``send()`` (or two
  sends) attached a duplicate ``text/html`` alternative
* rewrite the test suite in plain pytest style and extend it to cover settings
  precedence, template inheritance, context rendering, header handling,
  ``fail_silently`` forwarding and message serialization

---------------------
`1.1.1`_ (2018-02-01)
---------------------

* Bugfix: ``from_email`` does not fallback to ``DEFAULT_FROM_EMAIL``


---------------------
`1.1.0`_ (2018-01-29)
---------------------

* Add support for ``reply_to`` parameter in ``BaseEmailMessage.send`` method
* Add support for ``from_email`` parameter in ``BaseEmailMessage.send`` method
* Add support for Django 2.0
* Remove support for Django 1.10
* Fix passing context to email classes with context provided via mixin
* Fix invalid release years in release notes

---------------------
`1.0.0`_ (2017-10-06)
---------------------

* Breaking API: Update ``set_context_data`` to ``get_context_data``
* Add basic documentation
* Add basic examples
* Update templates rendering to happen on send
* Update dependencies
* Remove Python 3.3 from supported versions

---------------------
`0.2.0`_ (2017-09-22)
---------------------

* Add support for CC and BCC
* Update name of ``BaseEmailMessage.send_to`` to ``BaseEmailMessage.send``

---------------------
`0.1.1`_ (2017-09-15)
---------------------

* Bugfix: Issue with template nodes requiring template to be bound to context
* Bugfix: Issue with whitespaces around content blocks

---------------------
`0.1.0`_ (2017-09-15)
---------------------

* Initial release of the project. Its goal is to provide simple API for sending
  emails using Django template system. For more information and to get started see
  `README <https://github.com/sunscrapers/django-templated-mail/blob/0.1.0/README.rst>`_.


.. _0.1.0: https://github.com/sunscrapers/django-templated-mail/compare/3bc71b3...0.1.0
.. _0.1.1: https://github.com/sunscrapers/django-templated-mail/compare/0.1.0...0.1.1
.. _0.2.0: https://github.com/sunscrapers/django-templated-mail/compare/0.1.1...0.2.0
.. _1.0.0: https://github.com/sunscrapers/django-templated-mail/compare/0.2.0...1.0.0
.. _1.1.0: https://github.com/sunscrapers/django-templated-mail/compare/1.0.0...1.1.0
.. _1.1.1: https://github.com/sunscrapers/django-templated-mail/compare/1.1.0...1.1.1
.. _2.0.0: https://github.com/sunscrapers/django-templated-mail/compare/1.1.1...2.0.0

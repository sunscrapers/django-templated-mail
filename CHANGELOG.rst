==========
Change Log
==========

This document records all notable changes to django-templated-mail.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

---------------------
`1.1.0`_ (2017-01-29)
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
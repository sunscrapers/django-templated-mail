Settings
========

You may optionally provide following settings:

.. code-block:: python

    DOMAIN = 'example.com'
    SITE_NAME = 'Foo Website'
    PROTOCOL = 'https'

Each of them can also be overridden per message by passing the same key in the
``context`` argument of ``BaseEmailMessage``.

DOMAIN
------

Used in email template context. In most cases it is used to simplify building URLs,
when frontend and backend are hosted under different address'. If not provided
the current site's domain is used when the message was given a ``request``, and
an empty string otherwise.


**Required**: ``False``

SITE_NAME
---------

Used in email template context. Usually it will contain the desired title of your
app. If not provided the current site's name is used when the message was given a
``request``, and an empty string otherwise.


**Required**: ``False``

PROTOCOL
--------

Used in email template context. Set it to ``https`` when your frontend is served
over TLS but the request that triggers the email is not (for example behind a
proxy that terminates TLS). If not provided it is derived from the request
(``https`` for secure requests, ``http`` otherwise) and defaults to ``http``
when there is no request.


**Required**: ``False``

Settings
========

You may optionally provide following settings:

.. code-block:: python

'TEMPLATED_MAIL': {
    'DOMAIN': 'example.com',
    'SITE_NAME': 'Foo Website',
    LOCALE_FIELD: 'locale',
}


DOMAIN
------

Used in email template context. In most cases it is used to simplify building URLs,
when frontend and backend are hosted under different address'. If not provided
the current site's domain will be used.


**Required**: ``False``

SITE_NAME
---------

Used in email template context. Usually it will contain the desired title of your
app. If not provided the current site's name will be used.


**Required**: ``False``

LOCALE_FIELD
------------------

The field on a user model that contains the locale name to be used. If not
specified, the per-user i18n is disabled.

**Required**: ``False``

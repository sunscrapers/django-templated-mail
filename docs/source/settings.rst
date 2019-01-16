Settings
========

You may optionally provide following settings:

.. code-block:: python

    'DOMAIN': 'example.com'
    'SITE_NAME': 'Foo Website'
    'TEMPLATE_ATTRIBUTE': 'django_template_name'

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


**Default**: ``False``

TEMPLATE_ATTRIBUTE
---------

It can happen that the attribute ``template_name`` causes problems when sending
e-mail. This will happen e.g. when you send your e-mail by ``django-anymail``
with Mandrill backend. In this case this attribute would be interpreted as
Mandrill's template. In cases like this you can change change the name of the
attribute to something that doesn't cause conflict.


**Default**: ``template_name``

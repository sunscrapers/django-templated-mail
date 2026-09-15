Templates syntax
================

Email templates can be built using three simple blocks:

- ``subject`` - used for subject of an email message
- ``text_body`` - used for plaintext body of an email message (not required)
- ``html_body`` - used for html body of an email message (not required)

Examples
--------

.. code-block:: html

    {% block subject %}Text and HTML mail subject{% endblock %}

    {% block text_body %}Foobar email content{% endblock %}

.. code-block:: html

    {% block subject %}Text and HTML mail subject{% endblock %}

    {% block text_body %}Foobar email content{% endblock %}
    {% block html_body %}<p>Foobar email content</p>{% endblock %}

Template inheritance
--------------------

Email templates can ``{% extends %}`` a base template and override any of the
blocks, including with ``{{ block.super }}``. Only the three blocks above are
read; other blocks in the base template are ignored.

.. code-block:: html

    {# base_mail.html #}
    {% block subject %}Notification{% endblock %}
    {% block text_body %}Hello {{ user }}{% endblock %}

    {# welcome_mail.html #}
    {% extends "base_mail.html" %}

    {% block subject %}Welcome: {{ block.super }}{% endblock %}
    {% block text_body %}{{ block.super }}, thanks for joining!{% endblock %}

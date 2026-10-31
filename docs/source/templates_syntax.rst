Templates syntax
================

Email templates can be built using three simple blocks:

- ``subject`` - used for subject of an email message; if it renders to several
  lines they are joined with spaces, since email headers cannot contain line breaks
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
read. Blocks nested inside them are rendered as part of them and can be
overridden as well; blocks outside them are ignored.

.. code-block:: html

    {# base_mail.html #}
    {% block subject %}Notification{% endblock %}
    {% block text_body %}Hello {{ user }}{% endblock %}

    {# welcome_mail.html #}
    {% extends "base_mail.html" %}

    {% block subject %}Welcome: {{ block.super }}{% endblock %}
    {% block text_body %}{{ block.super }}, thanks for joining!{% endblock %}

A nested block lets several emails share one HTML layout and fill in only
their own part of it:

.. code-block:: html

    {# layout_mail.html #}
    {% block html_body %}<html><body>{% block content %}{% endblock %}</body></html>{% endblock %}

    {# reset_mail.html #}
    {% extends "layout_mail.html" %}

    {% block subject %}Reset your password{% endblock %}
    {% block content %}<p>Follow the link to choose a new password.</p>{% endblock %}

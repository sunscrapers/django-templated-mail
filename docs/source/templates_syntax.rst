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

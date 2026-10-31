Sample usage
============

At first let's discuss the simplest possible use case, where you just wish to
send an email to a given address and using the given template.

.. code-block:: python

    from templated_mail.mail import BaseEmailMessage

    BaseEmailMessage(template_name='email.html').send(to=['foo@bar.tld'])

This one-liner will do all of the work required to render proper template blocks
and assign the results to proper email pieces. It will also determine appropriate
content type (including support for MIME) and send the output message to provided
list of email address'.

You might also wish to define your own subclass of
``templated_mail.mail.BaseEmailMessage`` to customize a thing or two.
What might be most interesting for you is the ``get_context_data`` method,
which returns context used during template rendering.

.. code-block:: python

    class MyEmailMessage(BaseEmailMessage):
        def get_context_data(self):
            context = super().get_context_data()
            context['foo'] = 'bar'
            return context

You might also provide custom context data using the ``context`` parameter.

.. code-block:: python

    from templated_mail.mail import BaseEmailMessage

    BaseEmailMessage(context={'foo': 'bar'}, template_name='email.html').send(to=['foo@bar.tld'])

In other cases you might notice that some of your emails use common ``template_name``
and so to save some space you might wish to override the base class' attribute.

.. code-block:: python

    class MyEmailMessage(BaseEmailMessage):
        template_name = 'email.html'

Rendering happens once
----------------------

A message instance renders its templates the first time ``render()`` or
``send()`` is called and keeps the result. Sending the same instance again
reuses the rendered subject and bodies, so build a new instance when you need
different context. Once ``send()`` has run, the ``request`` passed to the
constructor is dropped from the instance so that the message can be pickled or
deep-copied, for example by task queues or by Django's in-memory test backend.

Personalizing e-mails
========================



Interpolating user data
------------------------------

If you want to put some personal data of your user in the e-mail, you may use
the ``user`` variable in your context. To use this variable you either need to
pass the ``request`` object when creating the ``BaseEmailMessage``:

.. code-block:: python
    email_message = BaseEmailMessage(
        request=request,
        template_name='personalized_mail.html'
    )

or you need to specify actual user objects in the `to` field:

.. code-block:: python
    email_message.send(to=[user1, user2], single_email=False)

i18n
------

Django features some pretty nice i18n mechanism, but it can be insufficient
when emailing your users. Your e-mails will ofter be sent from inside a celery
task, where the ``request`` object is not accessible. If you still want to
translate the e-mail for your userbase, you need to specify the `locale_field`
value in your settings. This value should point to a field (or a property)
on your user models that contains their locale (it is up to you,
how do you populate this field). If you then send personalized emails, as
described above, they will be translated to your users' locales.

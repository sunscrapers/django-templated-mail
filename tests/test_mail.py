try:
    from unittest import mock
except ImportError:
    import mock

from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.test import RequestFactory, TestCase
from templated_mail.mail import BaseEmailMessage


class TestBaseEmailMessage(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.recipients = ['foo@bar.tld']

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_secure')
    def test_get_context_data_with_insecure_request(self, is_secure_mock):
        is_secure_mock.return_value = False

        request = self.factory.get('/')
        request.user = AnonymousUser()

        email_message = BaseEmailMessage(
            request=request, template_name='text_mail.html'
        )
        context = email_message.get_context_data()
        site = get_current_site(request)

        self.assertEquals(context['domain'], site.domain)
        self.assertEquals(context['protocol'], 'http')
        self.assertEquals(context['site_name'], site.name)
        self.assertEquals(context['user'], request.user)

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_secure')
    def test_get_context_data_with_secure_request(self, is_secure_mock):
        is_secure_mock.return_value = True

        request = self.factory.get('/')
        request.user = AnonymousUser()

        email_message = BaseEmailMessage(
            request=request, template_name='text_mail.html'
        )
        context = email_message.get_context_data()
        site = get_current_site(request)

        self.assertEquals(context['domain'], site.domain)
        self.assertEquals(context['protocol'], 'https')
        self.assertEquals(context['site_name'], site.name)
        self.assertEquals(context['user'], request.user)

    def test_get_context_data_without_request_no_context(self):
        email_message = BaseEmailMessage(template_name='text_mail.html')
        context = email_message.get_context_data()

        self.assertEquals(context['domain'], '')
        self.assertEquals(context['protocol'], 'http')
        self.assertEquals(context['site_name'], '')
        self.assertEquals(context['user'], None)

    def test_get_context_data_without_request_user_context(self):
        user = AnonymousUser()
        email_message = BaseEmailMessage(
            context={'user': user}, template_name='text_mail.html'
        )
        context = email_message.get_context_data()

        self.assertEquals(context['domain'], '')
        self.assertEquals(context['protocol'], 'http')
        self.assertEquals(context['site_name'], '')
        self.assertEquals(context['user'], user)

    def test_text_mail_contains_valid_data(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        BaseEmailMessage(
            request=request, template_name='text_mail.html'
        ).send(to=self.recipients)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), self.recipients)
        self.assertEqual(mail.outbox[0].subject, 'Text mail subject')
        self.assertEqual(mail.outbox[0].body, 'Foobar email content')
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, 'plain')

    def test_html_mail_contains_valid_data(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        BaseEmailMessage(
            request=request, template_name='html_mail.html'
        ).send(to=self.recipients)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), self.recipients)
        self.assertEqual(mail.outbox[0].subject, 'HTML mail subject')
        self.assertEqual(mail.outbox[0].body, '<p>Foobar email content</p>')
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, 'html')

    def test_text_and_html_mail_contains_valid_data(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        BaseEmailMessage(
            request=request, template_name='text_and_html_mail.html'
        ).send(to=self.recipients)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), self.recipients)
        self.assertEqual(mail.outbox[0].subject, 'Text and HTML mail subject')
        self.assertEqual(mail.outbox[0].body, 'Foobar email content')
        self.assertEqual(
            mail.outbox[0].alternatives,
            [('<p>Foobar email content</p>', 'text/html')]
        )
        self.assertEqual(mail.outbox[0].content_subtype, 'plain')

    def test_can_send_mail_with_none_request(self):
        BaseEmailMessage(
            request=None, template_name='text_mail.html'
        ).send(to=self.recipients)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), self.recipients)
        self.assertEqual(mail.outbox[0].subject, 'Text mail subject')
        self.assertEqual(mail.outbox[0].body, 'Foobar email content')
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, 'plain')

    def test_mail_cc_is_sent_to_valid_cc(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        cc = ['email@example.tld']

        BaseEmailMessage(
            request=request, template_name='text_mail.html'
        ).send(to=self.recipients, cc=cc)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, self.recipients)
        self.assertEqual(mail.outbox[0].cc, cc)
        self.assertEqual(mail.outbox[0].subject, 'Text mail subject')
        self.assertEqual(mail.outbox[0].body, 'Foobar email content')
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, 'plain')

    def test_mail_bcc_is_sent_to_valid_bcc(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        bcc = ['email@example.tld']

        BaseEmailMessage(
            request=request, template_name='text_mail.html'
        ).send(to=self.recipients, bcc=bcc)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, self.recipients)
        self.assertEqual(mail.outbox[0].bcc, bcc)
        self.assertEqual(mail.outbox[0].subject, 'Text mail subject')
        self.assertEqual(mail.outbox[0].body, 'Foobar email content')
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, 'plain')

    def test_mail_reply_to_is_sent_with_valid_reply_to(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        reply_to = ['email@example.tld']

        BaseEmailMessage(
            request=request, template_name='text_mail.html'
        ).send(to=self.recipients, reply_to=reply_to)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, self.recipients)
        self.assertEqual(mail.outbox[0].reply_to, reply_to)
        self.assertEqual(mail.outbox[0].subject, 'Text mail subject')
        self.assertEqual(mail.outbox[0].body, 'Foobar email content')
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, 'plain')

    def test_mail_from_email_is_sent_with_valid_from_email(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        from_email = ['email@example.tld']

        BaseEmailMessage(
            request=request, template_name='text_mail.html'
        ).send(to=self.recipients, from_email=from_email)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, self.recipients)
        self.assertEqual(mail.outbox[0].from_email, from_email)
        self.assertEqual(mail.outbox[0].subject, 'Text mail subject')
        self.assertEqual(mail.outbox[0].body, 'Foobar email content')
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, 'plain')

from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.test import RequestFactory, TestCase

from templated_mail.mail import BaseEmailMessage


class EmailMessage(BaseEmailMessage):
    pass


class TestBaseEmailMessage(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.recipients = ['foo@bar.tld']

    def test_text_mail_contains_valid_data(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        EmailMessage.template_name = 'text_mail.html'
        EmailMessage(request=request).send_to(recipients=self.recipients)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), self.recipients)
        self.assertEqual(mail.outbox[0].subject, 'Text mail subject')
        self.assertEqual(mail.outbox[0].body, 'Foobar email content')
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, 'plain')

    def test_html_mail_contains_valid_data(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        EmailMessage.template_name = 'html_mail.html'
        EmailMessage(request=request).send_to(recipients=self.recipients)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), self.recipients)
        self.assertEqual(mail.outbox[0].subject, 'HTML mail subject')
        self.assertEqual(mail.outbox[0].body, '<p>Foobar email content</p>')
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, 'html')

    def test_text_and_html_mail_contains_valid_data(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        EmailMessage.template_name = 'text_and_html_mail.html'
        EmailMessage(request=request).send_to(recipients=self.recipients)
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
        EmailMessage.template_name = 'text_mail.html'
        EmailMessage(request=None).send_to(recipients=self.recipients)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), self.recipients)
        self.assertEqual(mail.outbox[0].subject, 'Text mail subject')
        self.assertEqual(mail.outbox[0].body, 'Foobar email content')
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, 'plain')

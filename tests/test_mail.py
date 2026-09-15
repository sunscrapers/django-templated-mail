import copy
import pickle
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.test import override_settings, RequestFactory, TestCase
from templated_mail.mail import BaseEmailMessage

from .helpers import MockMail


class TestBaseEmailMessage(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.recipients = ["foo@bar.tld"]

    @mock.patch("django.core.handlers.wsgi.WSGIRequest.is_secure")
    def test_get_context_data_with_insecure_request(self, is_secure_mock):
        is_secure_mock.return_value = False

        request = self.factory.get("/")
        request.user = AnonymousUser()

        email_message = BaseEmailMessage(
            request=request, template_name="text_mail.html"
        )
        context = email_message.get_context_data()
        site = get_current_site(request)

        self.assertEqual(context["domain"], site.domain)
        self.assertEqual(context["protocol"], "http")
        self.assertEqual(context["site_name"], site.name)
        self.assertEqual(context["user"], request.user)

    @mock.patch("django.core.handlers.wsgi.WSGIRequest.is_secure")
    def test_get_context_data_with_secure_request(self, is_secure_mock):
        is_secure_mock.return_value = True

        request = self.factory.get("/")
        request.user = AnonymousUser()

        email_message = BaseEmailMessage(
            request=request, template_name="text_mail.html"
        )
        context = email_message.get_context_data()
        site = get_current_site(request)

        self.assertEqual(context["domain"], site.domain)
        self.assertEqual(context["protocol"], "https")
        self.assertEqual(context["site_name"], site.name)
        self.assertEqual(context["user"], request.user)

    @override_settings(PROTOCOL="https")
    def test_protocol_setting_overrides_request_protocol(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        email_message = BaseEmailMessage(
            request=request, template_name="text_mail.html"
        )
        context = email_message.get_context_data()

        self.assertEqual(context["protocol"], "https")

    @override_settings(PROTOCOL="https")
    def test_protocol_setting_is_used_without_request(self):
        email_message = BaseEmailMessage(template_name="text_mail.html")
        context = email_message.get_context_data()

        self.assertEqual(context["protocol"], "https")

    @override_settings(PROTOCOL="https")
    def test_protocol_from_context_overrides_protocol_setting(self):
        email_message = BaseEmailMessage(
            context={"protocol": "ftp"}, template_name="text_mail.html"
        )
        context = email_message.get_context_data()

        self.assertEqual(context["protocol"], "ftp")

    def test_get_context_data_without_request_no_context(self):
        email_message = BaseEmailMessage(template_name="text_mail.html")
        context = email_message.get_context_data()

        self.assertEqual(context["domain"], "")
        self.assertEqual(context["protocol"], "http")
        self.assertEqual(context["site_name"], "")
        self.assertEqual(context["user"], None)

    def test_get_context_data_without_request_user_context(self):
        user = AnonymousUser()
        email_message = BaseEmailMessage(
            context={"user": user}, template_name="text_mail.html"
        )
        context = email_message.get_context_data()

        self.assertEqual(context["domain"], "")
        self.assertEqual(context["protocol"], "http")
        self.assertEqual(context["site_name"], "")
        self.assertEqual(context["user"], user)

    def test_text_mail_contains_valid_data(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        BaseEmailMessage(request=request, template_name="text_mail.html").send(
            to=self.recipients
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), self.recipients)
        self.assertEqual(mail.outbox[0].subject, "Text mail subject")
        self.assertEqual(mail.outbox[0].body, "Foobar email content")
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, "plain")

    def test_html_mail_contains_valid_data(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        BaseEmailMessage(request=request, template_name="html_mail.html").send(
            to=self.recipients
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), self.recipients)
        self.assertEqual(mail.outbox[0].subject, "HTML mail subject")
        self.assertEqual(mail.outbox[0].body, "<p>Foobar email content</p>")
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, "html")

    def test_text_and_html_mail_contains_valid_data(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        BaseEmailMessage(request=request, template_name="text_and_html_mail.html").send(
            to=self.recipients
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), self.recipients)
        self.assertEqual(mail.outbox[0].subject, "Text and HTML mail subject")
        self.assertEqual(mail.outbox[0].body, "Foobar email content")
        self.assertEqual(
            mail.outbox[0].alternatives, [("<p>Foobar email content</p>", "text/html")]
        )
        self.assertEqual(mail.outbox[0].content_subtype, "plain")

    def test_can_send_mail_with_none_request(self):
        BaseEmailMessage(request=None, template_name="text_mail.html").send(
            to=self.recipients
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), self.recipients)
        self.assertEqual(mail.outbox[0].subject, "Text mail subject")
        self.assertEqual(mail.outbox[0].body, "Foobar email content")
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, "plain")

    def test_mail_cc_is_sent_to_valid_cc(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        cc = ["email@example.tld"]

        BaseEmailMessage(request=request, template_name="text_mail.html").send(
            to=self.recipients, cc=cc
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, self.recipients)
        self.assertEqual(mail.outbox[0].cc, cc)
        self.assertEqual(mail.outbox[0].subject, "Text mail subject")
        self.assertEqual(mail.outbox[0].body, "Foobar email content")
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, "plain")

    def test_mail_bcc_is_sent_to_valid_bcc(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        bcc = ["email@example.tld"]

        BaseEmailMessage(request=request, template_name="text_mail.html").send(
            to=self.recipients, bcc=bcc
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, self.recipients)
        self.assertEqual(mail.outbox[0].bcc, bcc)
        self.assertEqual(mail.outbox[0].subject, "Text mail subject")
        self.assertEqual(mail.outbox[0].body, "Foobar email content")
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, "plain")

    def test_mail_reply_to_is_sent_with_valid_reply_to(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        reply_to = ["email@example.tld"]

        BaseEmailMessage(request=request, template_name="text_mail.html").send(
            to=self.recipients, reply_to=reply_to
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, self.recipients)
        self.assertEqual(mail.outbox[0].reply_to, reply_to)
        self.assertEqual(mail.outbox[0].subject, "Text mail subject")
        self.assertEqual(mail.outbox[0].body, "Foobar email content")
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, "plain")

    def test_mail_from_email_is_sent_with_valid_from_email(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        from_email = "<Example - email@example.tld>"

        BaseEmailMessage(request=request, template_name="text_mail.html").send(
            to=self.recipients, from_email=from_email
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, self.recipients)
        self.assertEqual(mail.outbox[0].from_email, from_email)
        self.assertEqual(mail.outbox[0].subject, "Text mail subject")
        self.assertEqual(mail.outbox[0].body, "Foobar email content")
        self.assertEqual(mail.outbox[0].alternatives, [])
        self.assertEqual(mail.outbox[0].content_subtype, "plain")

    @override_settings(DEFAULT_FROM_EMAIL="default@example.tld")
    def test_mail_without_from_email_is_sent_with_valid_from_email(self):
        BaseEmailMessage(request=None, template_name="text_mail.html").send(
            to=self.recipients
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, self.recipients)
        self.assertEqual(mail.outbox[0].from_email, "default@example.tld")

    def test_sent_message_can_be_deep_copied_and_pickled(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        # Stands in for the ResolverMatch a real request carries, which is
        # what made messages fail to copy in production.
        request.resolver_match = (_ for _ in ())

        email_message = BaseEmailMessage(
            request=request, template_name="text_mail.html"
        )
        email_message.send(to=self.recipients)

        # Django >= 5.1 deep copies every message handed to the locmem
        # backend, and task queues pickle messages; a request is neither
        # deep-copyable nor picklable.
        message_copy = copy.deepcopy(email_message)
        unpickled = pickle.loads(pickle.dumps(email_message))

        self.assertEqual(message_copy.body, "Foobar email content")
        self.assertEqual(unpickled.body, "Foobar email content")
        self.assertIsNone(email_message.request)

    def test_extending_mail_with_context_mixin(self):
        email_message = MockMail(template_name="text_mail.html", context={"foo": "bar"})

        context = email_message.get_context_data()

        self.assertEqual(context["foo"], "bar")
        self.assertEqual(context["thing"], 42)

    def test_extending_mail_template(self):
        email_message = BaseEmailMessage(template_name="extends.html")
        email_message.render()

        self.assertEqual(email_message.subject, "Text and HTML mail subject")
        self.assertEqual(email_message.body, "Foobar email content")
        self.assertEqual(email_message.html, "Some extended HTML body")

    def test_nested_extending_mail_template(self):
        email_message = BaseEmailMessage(template_name="nested_extends.html")
        email_message.render()

        self.assertEqual(email_message.subject, "Text and HTML mail subject")
        self.assertEqual(email_message.body, "Some extended text body")
        self.assertEqual(email_message.html, "Some extended HTML body")

import copy
import pickle

import django
import pytest
from django.core import mail

from templated_mail.mail import BaseEmailMessage


def send(recipients, template_name="text_mail.html", **kwargs):
    send_kwargs = {
        key: kwargs.pop(key)
        for key in list(kwargs)
        if key in {"cc", "bcc", "reply_to", "from_email", "fail_silently"}
    }
    email_message = BaseEmailMessage(template_name=template_name, **kwargs)
    result = email_message.send(to=recipients, **send_kwargs)
    return email_message, result


class TestDelivery:
    def test_text_mail(self, mailoutbox, recipients, http_request):
        send(recipients, request=http_request)

        assert len(mailoutbox) == 1
        message = mailoutbox[0]
        assert message.recipients() == recipients
        assert message.subject == "Text mail subject"
        assert message.body == "Foobar email content"
        assert message.alternatives == []
        assert message.content_subtype == "plain"

    def test_html_mail(self, mailoutbox, recipients, http_request):
        send(recipients, template_name="html_mail.html", request=http_request)

        message = mailoutbox[0]
        assert message.subject == "HTML mail subject"
        assert message.body == "<p>Foobar email content</p>"
        assert message.alternatives == []
        assert message.content_subtype == "html"
        assert message.message().get_content_type() == "text/html"

    def test_text_and_html_mail(self, mailoutbox, recipients, http_request):
        send(recipients, template_name="text_and_html_mail.html", request=http_request)

        message = mailoutbox[0]
        assert message.body == "Foobar email content"
        assert message.content_subtype == "plain"
        assert [tuple(alt) for alt in message.alternatives] == [
            ("<p>Foobar email content</p>", "text/html")
        ]
        mime = message.message()
        assert mime.get_content_type() == "multipart/alternative"
        assert [part.get_content_type() for part in mime.get_payload()] == [
            "text/plain",
            "text/html",
        ]

    def test_without_request(self, mailoutbox, recipients):
        send(recipients)

        assert len(mailoutbox) == 1
        assert mailoutbox[0].subject == "Text mail subject"

    def test_one_liner_from_docs(self, mailoutbox, recipients):
        BaseEmailMessage(template_name="text_mail.html").send(to=recipients)

        assert mailoutbox[0].recipients() == recipients

    def test_to_can_be_positional(self, mailoutbox, recipients):
        BaseEmailMessage(template_name="text_mail.html").send(recipients)

        assert mailoutbox[0].to == recipients

    def test_to_is_required(self):
        with pytest.raises(TypeError):
            BaseEmailMessage(template_name="text_mail.html").send()

    def test_returns_number_of_sent_messages(self, recipients):
        _, result = send(recipients)

        assert result == 1

    def test_each_send_renders_fresh_content(self, mailoutbox, recipients):
        email_message = BaseEmailMessage(
            template_name="context_mail.html", context={"payload": "first"}
        )
        email_message.send(to=recipients)
        first_body = email_message.body
        email_message.context["payload"] = "second"
        email_message.send(to=recipients)

        assert first_body.endswith("first")
        assert email_message.body.endswith("second")
        assert len(mailoutbox) == 2

    def test_render_then_send_sends_single_alternative(self, mailoutbox, recipients):
        email_message = BaseEmailMessage(template_name="text_and_html_mail.html")
        email_message.render()

        email_message.send(to=recipients)

        assert len(mailoutbox[0].alternatives) == 1


class TestHeaders:
    def test_cc(self, mailoutbox, recipients):
        send(recipients, cc=["cc@example.tld"])

        assert mailoutbox[0].to == recipients
        assert mailoutbox[0].cc == ["cc@example.tld"]
        assert mailoutbox[0].recipients() == recipients + ["cc@example.tld"]

    def test_bcc(self, mailoutbox, recipients):
        send(recipients, bcc=["bcc@example.tld"])

        assert mailoutbox[0].to == recipients
        assert mailoutbox[0].bcc == ["bcc@example.tld"]
        assert mailoutbox[0].recipients() == recipients + ["bcc@example.tld"]
        assert "bcc@example.tld" not in mailoutbox[0].message().as_string()

    def test_reply_to(self, mailoutbox, recipients):
        send(recipients, reply_to=["reply@example.tld"])

        assert mailoutbox[0].reply_to == ["reply@example.tld"]
        assert mailoutbox[0].message()["Reply-To"] == "reply@example.tld"

    def test_from_email(self, mailoutbox, recipients):
        send(recipients, from_email="Example <email@example.tld>")

        assert mailoutbox[0].from_email == "Example <email@example.tld>"

    def test_from_email_defaults_to_setting(self, settings, mailoutbox, recipients):
        settings.DEFAULT_FROM_EMAIL = "default@example.tld"

        send(recipients)

        assert mailoutbox[0].from_email == "default@example.tld"

    @pytest.mark.parametrize("header", ["cc", "bcc", "reply_to"])
    def test_headers_default_to_empty(self, mailoutbox, recipients, header):
        send(recipients)

        assert getattr(mailoutbox[0], header) == []

    def test_headers_are_reset_between_sends(self, mailoutbox, recipients):
        email_message = BaseEmailMessage(template_name="text_mail.html")
        email_message.send(to=recipients, cc=["cc@example.tld"])

        email_message.send(to=recipients)

        assert mailoutbox[1].cc == []

    def test_extra_headers_from_constructor(self, mailoutbox, recipients):
        send(recipients, headers={"X-Campaign": "welcome"})

        assert mailoutbox[0].extra_headers == {"X-Campaign": "welcome"}
        assert mailoutbox[0].message()["X-Campaign"] == "welcome"


class TestForwarding:
    def test_fail_silently_is_forwarded(self, mocker, recipients):
        send_mock = mocker.patch.object(mail.EmailMultiAlternatives, "send")

        BaseEmailMessage(template_name="text_mail.html").send(
            to=recipients, fail_silently=True
        )

        send_mock.assert_called_once_with(fail_silently=True)

    def test_fail_silently_defaults_to_django_default(self, mocker, recipients):
        send_mock = mocker.patch.object(mail.EmailMultiAlternatives, "send")

        BaseEmailMessage(template_name="text_mail.html").send(to=recipients)

        send_mock.assert_called_once_with()

    # Django 6.1 deprecates fail_silently in favour of mailers; forwarding it is
    # still the caller's choice, so only this test opts into the warning.
    @pytest.mark.filterwarnings("ignore:The 'fail_silently' argument is deprecated")
    def test_fail_silently_swallows_backend_errors(self, settings, recipients):
        backend = "tests.backends.FailingEmailBackend"
        if django.VERSION >= (6, 1):
            settings.MAILERS = {"default": {"BACKEND": backend}}
        else:
            settings.EMAIL_BACKEND = backend

        with pytest.raises(RuntimeError):
            send(recipients)
        _, result = send(recipients, fail_silently=True)

        assert result == 0


class TestSerialization:
    def test_request_is_dropped_after_send(self, recipients, http_request):
        email_message, _ = send(recipients, request=http_request)

        assert email_message.request is None

    def test_sent_message_can_be_deep_copied_and_pickled(self, recipients, http_request):
        # Stands in for the ResolverMatch a real request carries, which is
        # what made messages fail to copy in production (Django >= 5.1
        # deep copies every message handed to the locmem backend, and task
        # queues pickle them).
        http_request.resolver_match = (_ for _ in ())
        email_message, _ = send(recipients, request=http_request)

        message_copy = copy.deepcopy(email_message)
        unpickled = pickle.loads(pickle.dumps(email_message))

        assert message_copy.body == "Foobar email content"
        assert unpickled.body == "Foobar email content"
        assert unpickled.to == recipients

    def test_unsent_message_without_request_can_be_pickled(self):
        email_message = BaseEmailMessage(
            template_name="text_mail.html", context={"foo": "bar"}
        )

        unpickled = pickle.loads(pickle.dumps(email_message))

        assert unpickled.template_name == "text_mail.html"
        assert unpickled.context == {"foo": "bar"}

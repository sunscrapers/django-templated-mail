import pytest
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist

from templated_mail.mail import BaseEmailMessage

from .conftest import SubclassMail


def rendered(**kwargs):
    email_message = BaseEmailMessage(**kwargs)
    email_message.render()
    return email_message


class TestBlocks:
    def test_text_only(self):
        email_message = rendered(template_name="text_mail.html")

        assert email_message.subject == "Text mail subject"
        assert email_message.body == "Foobar email content"
        assert email_message.html is None
        assert email_message.alternatives == []
        assert email_message.content_subtype == "plain"

    def test_html_only_becomes_html_body(self):
        email_message = rendered(template_name="html_mail.html")

        assert email_message.subject == "HTML mail subject"
        assert email_message.body == "<p>Foobar email content</p>"
        assert email_message.html == "<p>Foobar email content</p>"
        assert email_message.alternatives == []
        assert email_message.content_subtype == "html"

    def test_text_and_html_attaches_alternative(self):
        email_message = rendered(template_name="text_and_html_mail.html")

        assert email_message.subject == "Text and HTML mail subject"
        assert email_message.body == "Foobar email content"
        assert email_message.content_subtype == "plain"
        assert [tuple(alt) for alt in email_message.alternatives] == [
            ("<p>Foobar email content</p>", "text/html")
        ]

    def test_missing_subject_block_leaves_subject_empty(self):
        email_message = rendered(template_name="no_subject.html")

        assert email_message.subject == ""
        assert email_message.body == "Body without subject"

    def test_subject_only_template(self):
        email_message = rendered(template_name="subject_only.html")

        assert email_message.subject == "Subject only"
        assert email_message.body == ""
        assert email_message.html is None
        assert email_message.alternatives == []

    def test_unknown_blocks_are_ignored(self):
        email_message = rendered(template_name="unknown_blocks.html")

        assert email_message.subject == "Known subject"
        assert email_message.body == "Known body"
        assert not hasattr(email_message, "header")
        assert not hasattr(email_message, "footer")

    def test_surrounding_whitespace_is_stripped(self):
        email_message = rendered(template_name="whitespace.html")

        assert email_message.subject == "Padded subject"
        assert email_message.body == "Padded body"

    def test_render_is_idempotent(self, mocker):
        email_message = rendered(template_name="text_and_html_mail.html")
        get_template = mocker.patch("templated_mail.mail.get_template")

        email_message.render()

        get_template.assert_not_called()
        assert len(email_message.alternatives) == 1

    def test_user_attached_alternatives_survive_render(self):
        email_message = BaseEmailMessage(template_name="text_and_html_mail.html")
        email_message.attach_alternative("BEGIN:VCALENDAR", "text/calendar")

        email_message.render()

        assert [tuple(alt) for alt in email_message.alternatives] == [
            ("BEGIN:VCALENDAR", "text/calendar"),
            ("<p>Foobar email content</p>", "text/html"),
        ]

    def test_render_does_not_send(self, mailoutbox):
        rendered(template_name="text_mail.html")

        assert mailoutbox == []


class TestInheritance:
    def test_child_overrides_single_block(self):
        email_message = rendered(template_name="extends.html")

        assert email_message.subject == "Text and HTML mail subject"
        assert email_message.body == "Foobar email content"
        assert email_message.html == "Some extended HTML body"

    def test_nested_inheritance(self):
        email_message = rendered(template_name="nested_extends.html")

        assert email_message.subject == "Text and HTML mail subject"
        assert email_message.body == "Some extended text body"
        assert email_message.html == "Some extended HTML body"

    def test_three_levels_deep(self):
        email_message = rendered(template_name="deep_extends.html")

        assert email_message.subject == "Deep subject"
        assert email_message.body == "Some extended text body"
        assert email_message.html == "Some extended HTML body"


class TestContextInTemplates:
    def test_context_variables_are_rendered(self, settings):
        settings.DOMAIN = "example.com"
        settings.SITE_NAME = "Example"
        settings.PROTOCOL = "https"

        email_message = rendered(
            template_name="context_mail.html",
            context={"user": "alice", "payload": "plain"},
        )

        assert email_message.subject == "Hello alice from Example"
        assert email_message.body == "https://example.com/ plain"
        assert email_message.html == '<a href="https://example.com/">plain</a>'

    def test_variables_are_autoescaped(self):
        email_message = rendered(
            template_name="context_mail.html", context={"payload": "<b>&</b>"}
        )

        assert "&lt;b&gt;&amp;&lt;/b&gt;" in email_message.body
        assert "&lt;b&gt;&amp;&lt;/b&gt;" in email_message.html

    def test_non_ascii_content(self):
        email_message = rendered(
            template_name="context_mail.html",
            context={"user": "Zażółć", "site_name": "Łódź", "payload": "gęślą jaźń ✉"},
        )

        assert email_message.subject == "Hello Zażółć from Łódź"
        assert email_message.body.endswith("gęślą jaźń ✉")

    def test_request_context_processors_run(self, http_request):
        email_message = rendered(
            request=http_request, template_name="request_mail.html"
        )

        assert email_message.body == "path=/"

    def test_without_request_the_request_variable_is_empty(self):
        email_message = rendered(template_name="request_mail.html")

        assert email_message.body == "path="


class TestTemplateName:
    def test_class_attribute(self):
        email_message = SubclassMail()
        email_message.render()

        assert email_message.subject == "Text mail subject"

    def test_argument_overrides_class_attribute(self):
        email_message = SubclassMail(template_name="html_mail.html")
        email_message.render()

        assert email_message.subject == "HTML mail subject"

    def test_none_argument_keeps_class_attribute(self):
        email_message = SubclassMail(template_name=None)

        assert email_message.template_name == "text_mail.html"

    def test_no_template_name_raises(self):
        with pytest.raises(ImproperlyConfigured, match="template_name"):
            rendered()

    def test_no_template_name_fails_before_sending(self, mailoutbox, recipients):
        with pytest.raises(ImproperlyConfigured):
            BaseEmailMessage().send(to=recipients)

        assert mailoutbox == []

    def test_missing_template_raises(self):
        with pytest.raises(TemplateDoesNotExist):
            rendered(template_name="does_not_exist.html")

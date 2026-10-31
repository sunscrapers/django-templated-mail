import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site

from templated_mail.mail import BaseEmailMessage

from .conftest import MixinMail, SubclassMail


def context_for(**kwargs):
    kwargs.setdefault("template_name", "text_mail.html")
    return BaseEmailMessage(**kwargs).get_context_data()


class TestWithRequest:
    def test_insecure_request(self, http_request):
        context = context_for(request=http_request)
        site = get_current_site(http_request)

        assert context["domain"] == site.domain
        assert context["protocol"] == "http"
        assert context["site_name"] == site.name
        assert context["user"] is http_request.user

    def test_secure_request(self, secure_request):
        context = context_for(request=secure_request)

        assert context["protocol"] == "https"

    def test_domain_setting_overrides_site(self, settings, http_request):
        settings.DOMAIN = "frontend.example.com"

        context = context_for(request=http_request)

        assert context["domain"] == "frontend.example.com"

    def test_site_name_setting_overrides_site(self, settings, http_request):
        settings.SITE_NAME = "Frontend"

        context = context_for(request=http_request)

        assert context["site_name"] == "Frontend"

    def test_protocol_setting_overrides_request_protocol(self, settings, http_request):
        settings.PROTOCOL = "https"

        context = context_for(request=http_request)

        assert context["protocol"] == "https"

    @pytest.mark.parametrize("setting", ["DOMAIN", "SITE_NAME", "PROTOCOL"])
    def test_empty_setting_falls_back_to_request(self, settings, http_request, setting):
        setattr(settings, setting, "")

        context = context_for(request=http_request)
        site = get_current_site(http_request)

        expected = {"DOMAIN": site.domain, "SITE_NAME": site.name, "PROTOCOL": "http"}
        assert context[setting.lower()] == expected[setting]

    @pytest.mark.parametrize(
        ("key", "value"),
        [("domain", "ctx.example.com"), ("site_name", "Ctx"), ("protocol", "ftp")],
    )
    def test_context_overrides_settings_and_site(
        self, settings, http_request, key, value
    ):
        settings.DOMAIN = "settings.example.com"
        settings.SITE_NAME = "Settings"
        settings.PROTOCOL = "https"

        context = context_for(request=http_request, context={key: value})

        assert context[key] == value

    def test_context_user_overrides_request_user(self, http_request):
        user = AnonymousUser()

        context = context_for(request=http_request, context={"user": user})

        assert context["user"] is user
        assert context["user"] is not http_request.user


class TestWithoutRequest:
    def test_defaults(self):
        context = context_for()

        assert context["domain"] == ""
        assert context["protocol"] == "http"
        assert context["site_name"] == ""
        assert context["user"] is None

    def test_user_from_context(self):
        user = AnonymousUser()

        context = context_for(context={"user": user})

        assert context["user"] is user

    def test_settings_are_used(self, settings):
        settings.DOMAIN = "frontend.example.com"
        settings.SITE_NAME = "Frontend"
        settings.PROTOCOL = "https"

        context = context_for()

        assert context["domain"] == "frontend.example.com"
        assert context["site_name"] == "Frontend"
        assert context["protocol"] == "https"

    @pytest.mark.parametrize(
        ("key", "value"),
        [("domain", "ctx.example.com"), ("site_name", "Ctx"), ("protocol", "ftp")],
    )
    def test_context_overrides_settings(self, settings, key, value):
        settings.DOMAIN = "settings.example.com"
        settings.SITE_NAME = "Settings"
        settings.PROTOCOL = "https"

        context = context_for(context={key: value})

        assert context[key] == value


class TestContextComposition:
    def test_custom_context_is_passed_through(self):
        context = context_for(context={"foo": "bar", "answer": 42})

        assert context["foo"] == "bar"
        assert context["answer"] == 42

    def test_kwargs_are_merged(self):
        email_message = BaseEmailMessage(template_name="text_mail.html")

        context = email_message.get_context_data(extra="value")

        assert context["extra"] == "value"

    def test_instance_context_wins_over_kwargs(self):
        email_message = BaseEmailMessage(
            template_name="text_mail.html", context={"key": "instance"}
        )

        context = email_message.get_context_data(key="kwarg")

        assert context["key"] == "instance"

    def test_instance_context_is_not_mutated(self):
        original = {"foo": "bar"}
        email_message = BaseEmailMessage(
            template_name="text_mail.html", context=original
        )

        email_message.get_context_data()

        assert original == {"foo": "bar"}
        assert email_message.context is original

    def test_view_points_at_message(self):
        # Inherited from ContextMixin; djoser pops it, so keep it explicit.
        email_message = BaseEmailMessage(template_name="text_mail.html")

        context = email_message.get_context_data()

        assert context["view"] is email_message

    def test_context_mixin(self):
        email_message = MixinMail(
            template_name="text_mail.html", context={"foo": "bar"}
        )

        context = email_message.get_context_data()

        assert context["foo"] == "bar"
        assert context["thing"] == 42

    def test_subclass_extends_context(self):
        context = SubclassMail().get_context_data()

        assert context["foo"] == "bar"
        assert context["protocol"] == "http"

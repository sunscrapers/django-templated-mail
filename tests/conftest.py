import pytest
from django.contrib.auth.models import AnonymousUser
from django.views.generic.base import ContextMixin

from templated_mail.mail import BaseEmailMessage


@pytest.fixture
def recipients():
    return ["foo@bar.tld"]


@pytest.fixture
def http_request(rf):
    request = rf.get("/")
    request.user = AnonymousUser()
    return request


@pytest.fixture
def secure_request(rf):
    request = rf.get("/", secure=True)
    request.user = AnonymousUser()
    return request


class ExtraContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["thing"] = 42
        return context


class MixinMail(BaseEmailMessage, ExtraContextMixin):
    pass


class SubclassMail(BaseEmailMessage):
    template_name = "text_mail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["foo"] = "bar"
        return context

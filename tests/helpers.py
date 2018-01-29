from django.views.generic.base import ContextMixin
from templated_mail.mail import BaseEmailMessage


class MockMailContext(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super(MockMailContext, self).get_context_data(**kwargs)
        context['thing'] = 42
        return context


class MockMail(BaseEmailMessage, MockMailContext):
    pass

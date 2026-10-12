from django.core.mail.backends.base import BaseEmailBackend


class FailingEmailBackend(BaseEmailBackend):
    # Django 6.1 expects a backend to consume fail_silently itself rather than
    # hand it to the base class, which deprecates the attribute.
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(**kwargs)
        self.swallow_errors = fail_silently

    def send_messages(self, email_messages):
        if self.swallow_errors:
            return 0
        raise RuntimeError("SMTP is down")

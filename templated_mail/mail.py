import copy
import contextlib
import six

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.utils import translation
from django.template.context import make_context
from django.template.loader import get_template
from django.template.loader_tags import BlockNode, ExtendsNode
from django.views.generic.base import ContextMixin


LOCALE_FIELD = getattr(
    settings, 'TEMPLATED_MAIL', {}
).get('locale_field', None)


@contextlib.contextmanager
def translation_context(language):
    prev_language = translation.get_language()
    try:
        translation.activate(language)
        yield
    finally:
        translation.activate(prev_language)


@contextlib.contextmanager
def nullcontext():
    yield


class BaseEmailMessage(mail.EmailMultiAlternatives, ContextMixin):
    _node_map = {
        'subject': 'subject',
        'text_body': 'body',
        'html_body': 'html',
    }
    template_name = None

    def __init__(self, request=None, context=None, template_name=None,
                 *args, **kwargs):
        super(BaseEmailMessage, self).__init__(*args, **kwargs)

        self.request = request
        self.context = {} if context is None else context
        self.html = None

        if template_name is not None:
            self.template_name = template_name
        self.is_rendered = False

    def get_context_data(self, user=None, **kwargs):
        ctx = super(BaseEmailMessage, self).get_context_data(**kwargs)
        context = dict(ctx, **self.context)
        if self.request:
            site = get_current_site(self.request)
            domain = context.get('domain') or (
                getattr(settings, 'DOMAIN', '') or site.domain
            )
            protocol = context.get('protocol') or (
                'https' if self.request.is_secure() else 'http'
            )
            site_name = context.get('site_name') or (
                getattr(settings, 'SITE_NAME', '') or site.name
            )
            user = user or context.get('user') or self.request.user
        else:
            domain = context.get('domain') or getattr(settings, 'DOMAIN', '')
            protocol = context.get('protocol') or 'http'
            site_name = context.get('site_name') or getattr(
                settings, 'SITE_NAME', ''
            )
            user = user or context.get('user')

        context.update({
            'domain': domain,
            'protocol': protocol,
            'site_name': site_name,
            'user': user
        })
        return context

    def render(self, user=None):
        if self.is_rendered:
            return
        context = make_context(
            self.get_context_data(user),
            request=self.request,
        )
        if user is None or LOCALE_FIELD is None:
            language_context = nullcontext()
        else:
            language_context = translation_context(
                getattr(user, LOCALE_FIELD)
            )
        template = get_template(self.template_name)
        with language_context, context.bind_template(template.template):
            blocks = self._get_blocks(template.template.nodelist, context)
            for block_node in blocks.values():
                self._process_block(block_node, context)
        self._attach_body()
        self.is_rendered = True

    def send(self, to, single_email=True, *args, **kwargs):
        if single_email:
            self.render()
            to_emails = []
            for recipient in to:
                if isinstance(recipient, AbstractBaseUser):
                    to_emails.append(recipient.email)
                elif isinstance(recipient, six.string_types):
                    to_emails.append(recipient)
                else:
                    raise TypeError(
                        'The `to` argument should contain strings or users'
                    )
            self.to = to_emails
            self.cc = kwargs.pop('cc', [])
            self.bcc = kwargs.pop('bcc', [])
            self.reply_to = kwargs.pop('reply_to', [])
            self.from_email = kwargs.pop(
                'from_email', settings.DEFAULT_FROM_EMAIL
            )
            super(BaseEmailMessage, self).send(*args, **kwargs)
        else:
            for recipient in to:
                email = copy.copy(self)
                if isinstance(recipient, AbstractBaseUser):
                    email_to = [recipient.email]
                    email.render(user=recipient)
                elif isinstance(recipient, six.string_types):
                    email_to = [recipient]
                    email.render()
                else:
                    raise TypeError(
                        'The `to` argument should contain strings or users'
                    )
                email.send(to=email_to, *args, **kwargs)

    def _process_block(self, block_node, context):
        attr = self._node_map.get(block_node.name)
        if attr is not None:
            setattr(self, attr, block_node.render(context).strip())

    def _get_blocks(self, nodelist, context):
        blocks = {}
        for node in nodelist:
            if isinstance(node, ExtendsNode):
                parent = node.get_parent(context)
                blocks.update(self._get_blocks(parent.nodelist, context))
        blocks.update({
            node.name: node for node in nodelist.get_nodes_by_type(BlockNode)
        })
        return blocks

    def _attach_body(self):
        if self.body and self.html:
            self.attach_alternative(self.html, 'text/html')
        elif self.html:
            self.body = self.html
            self.content_subtype = 'html'

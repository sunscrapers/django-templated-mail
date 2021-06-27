from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.template.context import make_context
from django.template.loader import get_template
from django.template.loader_tags import BlockNode, ExtendsNode
from django.views.generic.base import ContextMixin


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

        self.render()

    def get_context_data(self, **kwargs):
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
            user = context.get('user') or self.request.user
        else:
            domain = context.get('domain') or getattr(settings, 'DOMAIN', '')
            protocol = context.get('protocol') or 'http'
            site_name = context.get('site_name') or getattr(
                settings, 'SITE_NAME', ''
            )
            user = context.get('user')

        context.update({
            'domain': domain,
            'protocol': protocol,
            'site_name': site_name,
            'user': user
        })
        return context

    def render(self):
        context = make_context(self.get_context_data(), request=self.request)
        template = get_template(self.template_name)
        with context.bind_template(template.template):
            blocks = self._get_blocks(template.template.nodelist, context)
            for block_node in blocks.values():
                self._process_block(block_node, context)
        self._attach_body()

    def send(self, *args, **kwargs):
        if len(args) > 0:
            self.to = args[0]
        elif "to" in kwargs:
            self.to = kwargs.pop('to')

        self.cc = kwargs.pop('cc', [])
        self.bcc = kwargs.pop('bcc', [])
        self.reply_to = kwargs.pop('reply_to', [])
        self.from_email = kwargs.pop(
            'from_email', settings.DEFAULT_FROM_EMAIL
        )

        if hasattr(self, "request"):
            del self.request
        super(BaseEmailMessage, self).send(*args, **kwargs)

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

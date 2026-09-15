from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured
from django.core import mail
from django.template.context import make_context
from django.template.loader import get_template
from django.template.loader_tags import (
    BLOCK_CONTEXT_KEY,
    BlockContext,
    BlockNode,
    ExtendsNode,
)
from django.views.generic.base import ContextMixin


class BaseEmailMessage(mail.EmailMultiAlternatives, ContextMixin):
    _node_map = {
        "subject": "subject",
        "text_body": "body",
        "html_body": "html",
    }
    template_name = None

    def __init__(self, request=None, context=None, template_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = request
        self.context = {} if context is None else context
        self.html = None
        self._is_rendered = False

        if template_name is not None:
            self.template_name = template_name

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        context = dict(ctx, **self.context)
        if self.request:
            site = get_current_site(self.request)
            domain = context.get("domain") or (
                getattr(settings, "DOMAIN", "") or site.domain
            )
            protocol = context.get("protocol") or (
                getattr(settings, "PROTOCOL", "")
                or ("https" if self.request.is_secure() else "http")
            )
            site_name = context.get("site_name") or (
                getattr(settings, "SITE_NAME", "") or site.name
            )
            user = context.get("user") or self.request.user
        else:
            domain = context.get("domain") or getattr(settings, "DOMAIN", "")
            protocol = context.get("protocol") or (
                getattr(settings, "PROTOCOL", "") or "http"
            )
            site_name = context.get("site_name") or getattr(settings, "SITE_NAME", "")
            user = context.get("user")

        context.update(
            {
                "domain": domain,
                "protocol": protocol,
                "site_name": site_name,
                "user": user,
            }
        )
        return context

    def render(self):
        if self._is_rendered:
            return
        if self.template_name is None:
            raise ImproperlyConfigured(
                f"{type(self).__name__} requires either a definition of "
                "'template_name' or a 'template_name' argument."
            )
        context = make_context(self.get_context_data(), request=self.request)
        template = get_template(self.template_name)
        with context.bind_template(template.template):
            # Mirror what ExtendsNode.render does: collect every level's
            # blocks into a BlockContext so overrides and {{ block.super }}
            # resolve the same way they do in a full template render.
            block_context = BlockContext()
            self._collect_blocks(template.template, context, block_context)
            context.render_context[BLOCK_CONTEXT_KEY] = block_context
            for block_name, attr in self._node_map.items():
                block_node = block_context.get_block(block_name)
                if block_node is not None:
                    setattr(self, attr, block_node.render(context).strip())
        self._attach_body()
        self._is_rendered = True

    def send(self, to, *args, **kwargs):
        self.render()

        self.to = to
        self.cc = kwargs.pop("cc", [])
        self.bcc = kwargs.pop("bcc", [])
        self.reply_to = kwargs.pop("reply_to", [])
        self.from_email = kwargs.pop("from_email", settings.DEFAULT_FROM_EMAIL)

        # The request is only needed for rendering. Dropping it keeps the
        # message deep-copyable and picklable, which Django's locmem backend
        # (5.1+) and task queues rely on.
        self.request = None

        return super().send(*args, **kwargs)

    def _collect_blocks(self, template, context, block_context):
        nodelist = template.nodelist
        for node in nodelist:
            if isinstance(node, ExtendsNode):
                block_context.add_blocks(node.blocks)
                self._collect_blocks(node.get_parent(context), context, block_context)
                return
        block_context.add_blocks(
            {node.name: node for node in nodelist.get_nodes_by_type(BlockNode)}
        )

    def _attach_body(self):
        if self.body and self.html:
            self.attach_alternative(self.html, "text/html")
        elif self.html:
            self.body = self.html
            self.content_subtype = "html"

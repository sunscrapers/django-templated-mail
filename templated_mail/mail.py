from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.template.context import make_context
from django.template.loader import get_template

from django.conf import settings


class BaseEmailMessage(mail.EmailMultiAlternatives):
    _node_map = {
        'subject': 'subject',
        'text_body': 'body',
        'html_body': 'html',
    }
    template_name = None

    def __init__(self, request, context=None, *args, **kwargs):
        super(BaseEmailMessage, self).__init__(*args, **kwargs)

        self.request = request
        self.context = {} if context is None else context
        self.html = None

        if request is not None:
            self.set_context_data()
        self.render()

    def set_context_data(self):
        site = get_current_site(self.request)
        self.context.update({
            'domain': getattr(settings, 'DOMAIN', '') or site.domain,
            'protocol': self.context.get('protocol') or (
                'https' if self.request.is_secure() else 'http'),
            'site_name': getattr(settings, 'SITE_NAME', '') or site.name,
            'user': self.context.get('user') or self.request.user,
        })

    def render(self):
        context = make_context(self.context, request=self.request)
        template = get_template(self.template_name)
        with context.bind_template(template.template):
            for node in template.template.nodelist:
                self._process_node(node, context)
        self._attach_body()

    def send_to(self, recipients, *args, **kwargs):
        self.to = recipients
        super(BaseEmailMessage, self).send(*args, **kwargs)

    def _process_node(self, node, context):
        attr = self._node_map.get(getattr(node, 'name', ''))
        if attr is not None:
            setattr(self, attr, node.render(context).strip())

    def _attach_body(self):
        if self.body and self.html:
            self.attach_alternative(self.html, 'text/html')
        elif self.html:
            self.body = self.html
            self.content_subtype = 'html'

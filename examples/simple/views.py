from django.http import HttpResponse

from templated_mail.mail import BaseEmailMessage


class TextEmailMessage(BaseEmailMessage):
    template_name = 'text_mail.html'


class HTMLEmailMessage(BaseEmailMessage):
    template_name = 'html_mail.html'


class TextAndHTMLEmailMessage(BaseEmailMessage):
    template_name = 'text_and_html_mail.html'


def text_mail_view(request):
    recipients = ['foo@bar.tld']
    TextEmailMessage(request).send(to=recipients)
    return HttpResponse('Text mail has been sent.')


def html_mail_view(request):
    recipients = ['foo@bar.tld']
    HTMLEmailMessage(request).send(to=recipients)
    return HttpResponse('HTML mail has been sent.')


def text_and_html_mail_view(request):
    recipients = ['foo@bar.tld']
    TextAndHTMLEmailMessage(request).send(to=recipients)
    return HttpResponse('Text and HTML mail has been sent.')

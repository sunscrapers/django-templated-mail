from django.conf.urls import url

from simple import views


urlpatterns = [
    url(r'^mail/txt_and_html', views.text_and_html_mail_view),
    url(r'^mail/txt', views.text_mail_view),
    url(r'^mail/html', views.html_mail_view),
]

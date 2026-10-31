from django.urls import path

from simple import views

app_name = "simple"

urlpatterns = [
    path("mail/txt_and_html", views.text_and_html_mail_view),
    path("mail/txt", views.text_mail_view),
    path("mail/html", views.html_mail_view),
]

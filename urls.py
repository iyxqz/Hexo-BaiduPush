# coding: utf-8

from django.conf.urls import url
from django.views import static

import views

urlpatterns = [
    url(r'^$', views.login),
    url(r'^repush', views.repush),
    url(r'^logout', views.logout),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': 'static'}),

]

# coding: utf-8

import os

DEBUG = os.environ.get('LEANCLOUD_APP_ENV') != 'production'
ROOT_URLCONF = 'urls'
SECRET_KEY = 'replace-this-with-your-secret-key'
ALLOWED_HOSTS = ['*']
TIME_ZONE = 'Asia/Shanghai'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': ['templates'],
}]

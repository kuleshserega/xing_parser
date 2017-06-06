XING PARSER:

Used technologies: Django, Scrapy
Used DB: PostgreSQL

Run scrapyd:

local:
    DJANGO_SETTINGS_MODULE='xing_django.settings' XING_PROJECT_PATH='/home/user/public_html/xing-employees-search/xing_django' scrapyd

on server:
    DJANGO_SETTINGS_MODULE='xing_django.settings' XING_PROJECT_PATH='/home/ubuntu/xing_parser/xing_django' scrapyd
